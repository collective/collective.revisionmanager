# -*- coding: utf-8 -*-
from collective.revisionmanager import _
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.interfaces import IRevisionSettingsSchema
from math import log
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.batching import Batch
from plone.protect import CheckAuthenticator
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from six.moves import zip
from z3c.form import button
from z3c.form import form
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.browser import BrowserPage


class HistoriesListView(BrowserPage):

    render = ViewPageTemplateFile('histories.pt')

    # i18n
    size_states = {
        'approximate': _(u'approximate'),
        'inaccurate': _(u'inaccurate'),
        None: _(u'unknown')
    }
    js_confirm = _('Are you sure?')

    def _del_histories(self, keys):
        # necessary information for ZVC access
        hs = api.portal.get_tool('portal_historiesstorage')
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
        storage = api.portal.get_tool('portal_historiesstorage')
        cache = getUtility(IHistoryStatsCache)
        for history_id in keys:
            # currentVersion = len(storage.getHistory(history_id))
            while True:
                length = len(storage.getHistory(history_id, countPurged=False))
                if length <= numrevs:
                    break
                comment = 'purged'
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

    def size_state(self, sizestateid):
        """ return translated size state
        sizestateid is either 'approximate' or 'inaccurate',
        defined in Products.CMFEditions.ZVCStorageTool.ShadowHistory.getSize
        """
        return api.portal.translate(self.size_states.get(sizestateid))

    def js_confirmation(self):
        return api.portal.translate(self.js_confirm)

    def reverse(self):
        return '1' if self.request.get('reverse', '0') == '0' else '0'

    def _determine_sortkey(self):
        """ Which table column do we want to use for sorting?
        This is straightforward with the exception of the portal_type
        column (because there might be multiple possible working copies for a
        given history)

        return a function that can be used as the 'key' argument to 'sorted()'
        """
        sortby = self.request.get('sortby', 'history_id')
        if sortby != 'portal_type':
            sortkey = lambda d: d[sortby]  # noqa
        else:
            # XXX use the first candidate's portal_type, which
            # might not always be what the user expects
            sortkey = lambda d: d['wcinfos'][0]['portal_type']  # noqa
        return sortkey

    def __call__(self):
        form = self.request.form
        stats = getUtility(IHistoryStatsCache)
        if 'del_histories' in form:
            keys = [int(k[5:]) for k in form.get('delete', []) if k.startswith('check')]  # noqa: E501
            self._purge_n_revisions(keys, int(form['keepnum']))
        elif 'del_orphans' in form:
            keys = []
            histories = stats.get('histories', [])
            for history in histories:
                if len(history['wcinfos']) > 1:
                    continue
                wcinfo = history['wcinfos'][0]
                if wcinfo['url'] is None:
                    path = wcinfo['path']
                    if path.startswith('no working copy') or path == 'All revisions have been purged':
                        keys.append(history['history_id'])
            self._del_histories(keys)
        histories = stats.get('histories', [])
        sortkey = self._determine_sortkey()
        reverse = bool(int(self.request.get('reverse', 0)))
        self.batch = Batch(
            sequence=sorted(histories, key=sortkey, reverse=reverse),
            size=int(self.request.get('b_size', 30)),
            start=int(self.request.get('b_start', 0)),
            orphan=1)
        return self.render()

    def humanize_size(self, num):
        """Transform bytes into a human readable format."""
        if not num:
            return '0 bytes'
        if num == 1:
            return '1 byte'
        if num == '???':
            return '???'
        unit_list = list(zip(
            ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
            [0, 0, 1, 2, 2, 2]))
        if num > 1:
            exponent = min(int(log(num, 1024)), len(unit_list) - 1)
            quotient = float(num) / 1024**exponent
            unit, num_decimals = unit_list[exponent]
            format_string = '{:.%sf} {}' % (num_decimals)  # noqa: S001,P103
            return format_string.format(quotient, unit)


class RevisionsControlPanel(AutoExtensibleForm, form.EditForm):
    """ Revision settings
    """
    schema = IRevisionSettingsSchema
    id = 'evisions-control-panel'
    label = _('Revision settings')
    description = _('Revision history settings for this site.')
    form_name = _('Revision settings')
    control_panel_view = 'revisions-controlpanel'
    template = ViewPageTemplateFile('revisionssettings.pt')

    def __init__(self, *args, **kw):
        super(RevisionsControlPanel, self).__init__(*args, **kw)
        self.statscache = getUtility(IHistoryStatsCache)

    def available(self):
        # We used to check for the
        # AccessControl.Permissions.view_management_screens
        # permission on the *Zope* root, but that seems unneeded.
        # It is enough to check Manage Portal permission in zcml.
        # See https://github.com/collective/collective.revisionmanager/issues/30
        # Let's keep the method though, so people can override it.
        return True

    def summaries(self):
        return self.statscache.get('summaries')

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
            msg = _(u'text_not_allowed_manage_server',
                    default=u'You are not allowed to manage the Zope server.')
            api.portal.show_message(msg, self.request, type='error')
            return
        value = data.get('number_versions_to_keep', -1)
        ptool = api.portal.get_tool('portal_purgepolicy')
        ptool.maxNumberOfVersionsToKeep = value
        value = data.get('subtransaction_threshold', 0)
        cache = getUtility(IHistoryStatsCache)
        cache.subtransaction_threshold = value

    @button.buttonAndHandler(_(u'Recalculate Statistics'), name='recalculate')
    def handle_recalculate_stats(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            msg = _(u'text_not_allowed_manage_server',
                    default=u'You are not allowed to manage the Zope server.')
            api.portal.show_message(msg, self.request, type='error')
            return
        self.statscache.refresh()


@implementer(IRevisionSettingsSchema)
@adapter(IPloneSiteRoot)
class RevisionsControlPanelAdapter(object):
    """ Plone style schema adapter for CMFEditions configuration settings
    """

    def __init__(self, context):
        self.context = context

    def _get_zvc_storage_tool_statistics(self):
        """ lazy calculate storage statistics
        """
        return getUtility(IHistoryStatsCache)
    zvc_storage_tool_statistics = property(_get_zvc_storage_tool_statistics)

    def _set_number_versions_to_keep(self, val):
        ptool = api.portal.get_tool('portal_purgepolicy')
        ptool.maxNumberOfVersionsToKeep = val

    def _get_number_versions_to_keep(self):
        ptool = api.portal.get_tool('portal_purgepolicy')
        return ptool.maxNumberOfVersionsToKeep
    number_versions_to_keep = property(
        _get_number_versions_to_keep, _set_number_versions_to_keep)

    def _set_subtransaction_threshold(self, val):
        self.zvc_storage_tool_statistics.subtransaction_threshold = val

    def _get_subtransaction_threshold(self):
        return self.zvc_storage_tool_statistics.subtransaction_threshold
    subtransaction_threshold = property(
        _get_subtransaction_threshold, _set_subtransaction_threshold)
