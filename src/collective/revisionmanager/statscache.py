# -*- coding: utf-8 -*-
import logging
from DateTime.DateTime import DateTime
from plone import api
from Products.CMFUid.interfaces import IUniqueIdGenerator
from Products.CMFUid.UniqueIdHandlerTool import UID_ATTRIBUTE_NAME
from Products.CMFEditions.ZVCStorageTool import Removed
from .interfaces import IHistoryStatsCache
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from ZODB.POSException import POSKeyError
import transaction
from time import time
from zope.component import getUtility
from zope.interface import implements

log = logging.getLogger(__name__)


class HistoryStatsCache(PersistentMapping):

    implements(IHistoryStatsCache)

    last_updated = None
    subtransaction_threshold = 0

    def _unrestricted_query_objects(self, cmf_uid):
        """ return all catalogued objects with a given cmf_uid -
        CMFUid's UniqueHandlerTool will only return the first match.
        In theory, cmf_uid should be unique, but it sometimes isn't.
        """
        # convert the uid to the right format
        generator = getUtility(IUniqueIdGenerator)
        uid = generator.convert(cmf_uid)

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults({UID_ATTRIBUTE_NAME: uid})
        return [brain.getObject() for brain in brains]

    @staticmethod
    def _save_retrieve(htool, hid, length):
        """ we sometimes encounter inconsistent histories that raise
        POSKeyErrors because of missing blobs.
        In this case, try wether we can use a previous version for statistics
        """
        try:
            wrapper = htool.retrieve(hid).object
        except POSKeyError:
            log.warn('POSKeyError encountered trying to retrieve history {}'.format(hid))  # noqa
            wrapper = {
                'path': 'POSKeyError encountered!',
                'portal_type': '-'
                }
            for selector in range(length-1, -1, -1):
                try:
                    wrapper = htool.retrieve(hid, str(selector)).object
                except POSKeyError:
                    # bad luck - use previously defined fallback
                    pass
        return wrapper

    def _calculate_storage_statistics(self):
        """
        we calculate our own stats, because
        ZVCStorageTool.zmi_getStorageStatistics is not exactly what we need.
        """
        siteid = api.portal.get().getId()
        htool = api.portal.get_tool('portal_historiesstorage')
        starttime = time()
        # get all history ids (incl. such that were deleted in the portal)
        storage = htool._getShadowStorage(autoAdd=False)
        if storage is not None:
            historyids = storage._storage
        else:
            historyids = {}

        # collect interesting informations
        histories = []
        for hid in historyids.keys():
            log.info('processing history {}'.format(hid))
            history = htool.getHistory(hid)
            length = len(history)
            shadow_storage = htool._getShadowHistory(hid)
            size = 0
            size_state = "n/a"
            if shadow_storage is not None:
                size, size_state = shadow_storage.getSize()

            # There might be multiple possible working copies for a
            # given history, e.g. a discussion item will have the same cmf_uid
            # as the document being discussed. Determine all candidates.
            potential_working_copies = \
                self._unrestricted_query_objects(hid)
            wcinfos = []
            if potential_working_copies:
                for working_copy in potential_working_copies:
                    url = working_copy.absolute_url()
                    parts = url.split('/')
                    start = parts.index(siteid) + 1
                    wcinfos.append(dict(
                        url=url,
                        path='/{}'.format('/'.join(parts[start:])),
                        portal_type=working_copy.getPortalTypeName()
                        ))
            else:
                di = {'url': None, }
                wrapper = self._save_retrieve(htool, hid, length)
                if isinstance(wrapper, Removed):
                    di.update({
                        'path': 'All revisions have been purged',
                        'portal_type': '-'})
                else:
                    retrieved = wrapper.object
                    di.update({
                        'path': 'no working copy, object id: {}'.format(
                            retrieved.getId()),
                        'portal_type': retrieved.getPortalTypeName()})
                wcinfos.append(di)
            histdata = {
                "history_id": hid,
                "length": length,
                "wcinfos": wcinfos,
                "size": size,
                "size_state": size_state,
            }
            histories.append(histdata)
            if self.subtransaction_threshold and \
                    (len(histories) % self.subtransaction_threshold == 0):
                log.info('committing subtransaction')
                transaction.savepoint(optimistic=True)

        # collect history ids with still existing working copies
        exisiting_histories = 0
        existing_versions = 0
        deleted_histories = 0
        deleted_versions = 0
        for histdata in histories:
            if histdata['wcinfos'][0]['url'] is None:
                deleted_histories += 1
                deleted_versions += histdata["length"]
            else:
                exisiting_histories += 1
                existing_versions += histdata["length"]

        processingtime = "{:.2f}".format(time() - starttime)
        numhistories = exisiting_histories+deleted_histories
        versions = existing_versions+deleted_versions

        if numhistories:
            total_average = "{:.1f}".format(float(versions)/numhistories)
        else:
            total_average = "n/a"

        if exisiting_histories:
            existing_average = "{:.1f}".format(
                float(existing_versions)/exisiting_histories)
        else:
            existing_average = "n/a"

        if deleted_histories:
            deleted_average = "{:.1f}".format(
                float(deleted_versions)/deleted_histories)
        else:
            deleted_average = "n/a"

        return {
            "histories": histories,
            "summaries": {
                "time": processingtime,
                "total_histories": numhistories,
                "total_versions": versions,
                "total_average": total_average,
                "exisiting_histories": exisiting_histories,
                "existing_versions": existing_versions,
                "existing_average": existing_average,
                "deleted_histories": deleted_histories,
                "deleted_versions": deleted_versions,
                "deleted_average": deleted_average,
            }
        }

    def refresh(self):
        """ cache fresh statistics from portal_historiesstorage
        """
        self.clear()
        stats = self._calculate_storage_statistics()
        self['summaries'] = PersistentMapping(stats['summaries'])
        self['histories'] = PersistentList([PersistentMapping(d) for d
                                            in stats['histories']])
        self.last_updated = DateTime()


def cache_factory():
    c = HistoryStatsCache()
    return c
