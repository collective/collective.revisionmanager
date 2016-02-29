# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.revisionmanager.interfaces import \
    IHistoryStatsCache, IRevisionSettingsSchema
from plone.app.controlpanel.form import ControlPanelForm
from plone.batching import Batch
from zope.component import adapts, getUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.publisher.browser import BrowserPage, BrowserView


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


class RefreshStatsView(BrowserView):

    def __call__(self):
        stats = getUtility(IHistoryStatsCache)
        stats.refresh()
        self.request.response.redirect(
            '{}/@@revisions-controlpanel'.format(self.context.portal_url()))


class RevisionsControlPanel(ControlPanelForm):
    """ Revision settings
    """
    base_template = ControlPanelForm.template
    template = ViewPageTemplateFile('revisionssettings.pt')

    form_fields = FormFields(IRevisionSettingsSchema)

    label = _("Revision settings")
    description = _("Revision history settings for this site.")
    form_name = _("Revision settings")

    def __init__(self, *args, **kw):
        super(RevisionsControlPanel, self).__init__(*args, **kw)
        self.statscache = getUtility(IHistoryStatsCache)

    def summaries(self):
        return self.statscache['summaries']

    def last_updated(self):
        return self.statscache.last_updated


class RevisionsControlPanelAdapter(SchemaAdapterBase):
    """ Plone style schema adapter for CMFEditions configuration settings
    """
    adapts(IPloneSiteRoot)
    implements(IRevisionSettingsSchema)

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
