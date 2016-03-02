# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.revisionmanager.interfaces import \
    IHistoryStatsCache, IRevisionSettingsSchema
from z3c.form import form, button
from plone.autoform.form import AutoExtensibleForm
from plone.batching import Batch
from zope.component import adapts, getUtility
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from plone.protect import CheckAuthenticator


class HistoriesListView(BrowserPage):

    render = ViewPageTemplateFile('histories.pt')

    def _del_histories(self, keys):
        # necessary information for ZVC access
        hs = getToolByName(self.context, 'portal_historiesstorage')
        zvcr = hs._getZVCRepo()
        storage = hs._getShadowStorage(autoAdd=False)
        cached_stats = getUtility(IHistoryStatsCache)
        histories = storage._storage
        for key in keys:
            zvchistid, unused = hs._getZVCAccessInfo(key, 0, True)
            #  remove from shadow storage
            del histories[key]
            # remove ZVC log entries
            del zvcr._histories[zvchistid]
            # remove from cache
            cached = [h for h in cached_stats['histories']
                      if h['history_id'] == key][0]
            cached_stats['histories'].remove(cached)

    def _purge_n_revisions(self, keys, numrevs):
        """Purge all but the n most current versions
        """
        if numrevs < 1:
            # we delete the entire history because it's faster and
            # produces less footprint than purging
            return self._del_histories(keys)
        storage = getToolByName(self.context, 'portal_historiesstorage')
        cache = getUtility(IHistoryStatsCache)
        for history_id in keys:
            # currentVersion = len(storage.getHistory(history_id))
            while True:
                length = len(storage.getHistory(history_id, countPurged=False))
                if length <= numrevs:
                    break
                comment = "purged"
                storage.purge(
                    history_id,
                    0,
                    metadata={'sys_metadata': {'comment': comment}},
                    countPurged=False)
            # mark in cache - length remains unchanged,
            # but size will be reduced
            cached = [h for h in cache['histories']
                      if h['history_id'] == history_id][0]
            cached['size'] = '???'

    def reverse(self):
        return '1' if self.request.get('reverse', '0') == '0' else '0'

    def __call__(self):
        form = self.request.form
        if 'del_histories' in form:
            keys = [int(k[5:]) for k in form.keys() if k.startswith('check')]
            self._purge_n_revisions(keys, int(form['keepnum']))
        stats = getUtility(IHistoryStatsCache)
        histories = stats['histories']
        sortkey = lambda d: d[self.request.get('sortby', 'history_id')]
        reverse = bool(int(self.request.get('reverse', 0)))
        self.batch = Batch(
            sequence=sorted(histories, key=sortkey, reverse=reverse),
            size=30,
            start=int(self.request.get('b_start', 0)),
            orphan=1)
        return self.render()


class RevisionsControlPanel(AutoExtensibleForm, form.EditForm):
    """ Revision settings
    """
    schema = IRevisionSettingsSchema
    id = "revisions-control-panel"
    label = _("Revision settings")
    description = _("Revision history settings for this site.")
    form_name = _("Revision settings")
    control_panel_view = "revisions-controlpanel"
    template = ViewPageTemplateFile('revisionssettings.pt')

    def __init__(self, *args, **kw):
        super(RevisionsControlPanel, self).__init__(*args, **kw)
        self.statscache = getUtility(IHistoryStatsCache)

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)

    def summaries(self):
        return self.statscache['summaries']

    def last_updated(self):
        return self.statscache.last_updated

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handle_save_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                u'text_not_allowed_manage_server',
                default=u'You are not allowed to manage the Zope server.'
            )
            return
        value = data.get('number_versions_to_keep', -1)
        ptool = getToolByName(self.context, 'portal_purgepolicy')
        ptool.maxNumberOfVersionsToKeep = value

    @button.buttonAndHandler(_(u'Recalculate Statistics'), name='recalculate')
    def handle_recalculate_stats(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                u'text_not_allowed_manage_server',
                default=u'You are not allowed to manage the Zope server.'
            )
            return
        self.statscache.refresh()


class RevisionsControlPanelAdapter(object):
    """ Plone style schema adapter for CMFEditions configuration settings
    """
    adapts(IPloneSiteRoot)
    implements(IRevisionSettingsSchema)

    def __init__(self, context):
        self.context = context

    def _get_zvc_storage_tool_statistics(self):
        """ lazy calculate storage statistics
        """
        return getUtility(IHistoryStatsCache)
    zvc_storage_tool_statistics = property(_get_zvc_storage_tool_statistics)

    def _set_number_versions_to_keep(self, val):
        ptool = getToolByName(self.context, 'portal_purgepolicy')
        ptool.maxNumberOfVersionsToKeep = val

    def _get_number_versions_to_keep(self):
        ptool = getToolByName(self.context, 'portal_purgepolicy')
        return ptool.maxNumberOfVersionsToKeep
    number_versions_to_keep = property(
        _get_number_versions_to_keep, _set_number_versions_to_keep)
