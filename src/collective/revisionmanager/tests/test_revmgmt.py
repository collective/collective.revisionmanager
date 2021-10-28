# -*- coding: utf-8 -*-
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING
from DateTime.DateTime import DateTime
from logging import DEBUG
from logging import WARN
from OFS.SimpleItem import SimpleItem
from Products.CMFEditions.ArchivistTool import ObjectData
from testfixtures import LogCapture
from time import time
from ZODB.broken import BrokenModified
from ZODB.POSException import POSKeyError
from zope.component import getUtility

import unittest


class CMFDummy(SimpleItem):

    def modified(self):
        return self.modification_date

    def notifyModified(self):
        self.modification_date = DateTime()

    def __init__(self, id, cmfuid, effective=None, expires=None):
        now = DateTime()
        self.modification_date = now
        self.id = id
        self.cmf_uid = cmfuid
        self.effective = effective if effective is not None else \
            self.modification_date
        self.expires = expires

    def getPortalTypeName(self):
        return 'Dummy'


def build_metadata(comment):
    """helper - builds a metadata dict
    """
    return {'sys_metadata': {'comment': comment}}


class HistoryStatsCacheTests(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.portal_storage = self.portal.portal_historiesstorage

        cmf_uid = 1
        obj1 = CMFDummy('obj', cmf_uid)
        obj1.text = 'v1 of text'
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj1),
            metadata=build_metadata('saved v1'))

        obj2 = CMFDummy('obj', cmf_uid)
        obj2.text = 'v2 of text'
        self.portal_storage.save(
            cmf_uid,
            ObjectData(obj2),
            metadata=build_metadata('saved v2'))

        obj3 = CMFDummy('obj', cmf_uid)
        obj3.text = 'v3 of text'
        self.portal_storage.save(
            cmf_uid,
            ObjectData(obj3),
            metadata=build_metadata('saved v3'))

        obj4 = CMFDummy('obj', cmf_uid)
        obj4.text = 'v4 of text'
        self.portal._setObject('obj', obj4)
        self.portal.portal_catalog.indexObject(self.portal.obj)
        self.portal_storage.save(
            cmf_uid,
            ObjectData(obj4),
            metadata=build_metadata('saved v4'))

        cmf_uid = 2
        tomorrow = DateTime() + 1
        obj5 = CMFDummy('tomorrow', cmf_uid, effective=tomorrow)
        obj5.allowedRolesAndUsers = ['Anonymous']
        self.portal._setObject('tomorrow', obj5)
        self.portal.portal_catalog.indexObject(self.portal.tomorrow)
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj5),
            metadata=build_metadata('effective tomorrow'))

        cmf_uid = 3
        yesterday = DateTime() - 1
        obj6 = CMFDummy('yesterday', cmf_uid, expires=yesterday)
        obj6.allowedRolesAndUsers = ['Anonymous']
        self.portal._setObject('yesterday', obj6)
        self.portal.portal_catalog.indexObject(self.portal.yesterday)
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj6),
            metadata=build_metadata('expired yesterday'))

        cmf_uid = 4
        obj7 = CMFDummy('public', cmf_uid)
        obj7.text = 'visible for everyone'
        obj7.allowedRolesAndUsers = ['Anonymous']
        self.portal._setObject('public', obj7)
        self.portal.portal_catalog.indexObject(self.portal.public)
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj7),
            metadata=build_metadata('saved public'))

    def test_interface(self):
        cache = getUtility(IHistoryStatsCache)
        self.assertTrue(IHistoryStatsCache.providedBy(cache))

    def test_caching(self):
        self.maxDiff = None
        before = time()
        cache = getUtility(IHistoryStatsCache)
        cache.refresh()
        after = time()
        self.assertGreater(cache.last_updated, before)
        self.assertLess(cache.last_updated, after)
        got = cache
        expected = {
            'summaries': {
                'deleted_versions': 0,
                'existing_versions': 7,
                'deleted_histories': 0,
                'total_versions': 7,
                'existing_average': '1.8',
                'existing_histories': 4,
                'total_histories': 4,
                'deleted_average': 'n/a',
                'total_average': '1.8'},
            'histories': [
                {
                    'history_id': 1,
                    'length': 4,
                    'wcinfos': [{
                        'url': 'http://nohost/plone/obj',
                        'path': '/obj',
                        'portal_type': 'Dummy'}],
                    'size_state': 'approximate'
                }, {
                    'history_id': 2,
                    'length': 1,
                    'wcinfos': [{
                        'url': 'http://nohost/plone/tomorrow',
                        'path': '/tomorrow',
                        'portal_type': 'Dummy'}],
                    'size_state': 'approximate'
                }, {
                    'history_id': 3,
                    'length': 1,
                    'wcinfos': [{
                        'url': 'http://nohost/plone/yesterday',
                        'path': '/yesterday',
                        'portal_type': 'Dummy'}],
                    'size_state': 'approximate'
                }, {
                    'history_id': 4,
                    'length': 1,
                    'wcinfos': [{
                        'url': 'http://nohost/plone/public',
                        'path': '/public',
                        'portal_type': 'Dummy'}],
                    'size_state': 'approximate'}]}
        for k, v in expected['summaries'].items():
            self.assertEqual(got['summaries'][k], v)
        # the time needed to calculate stats may vary
        self.assertLess(float(got['summaries']['time']), 1)
        self.assertEqual(len(expected['histories']), len(got['histories']))
        for idx in range(len(expected['histories'])):
            e = expected['histories'][idx]
            g = got['histories'][idx]
            for k, v in e.items():
                self.assertEqual(g[k], v)
            # The actual size is not important and we want robust tests,
            # s. https://github.com/plone/Products.CMFEditions/issues/31
            self.assertGreater(g['size'], 0)

    def test_subtransaction_threshold(self):
        with LogCapture(
                'collective.revisionmanager.statscache', level=DEBUG) as log:
            cache = getUtility(IHistoryStatsCache)
            cache.subtransaction_threshold = 2
            cache.refresh()
            log.check(
                ('collective.revisionmanager.statscache', 'DEBUG', 'processing history 1'),  # noqa: E501
                ('collective.revisionmanager.statscache', 'DEBUG', 'processing history 2'),  # noqa: E501
                ('collective.revisionmanager.statscache', 'INFO', 'committing subtransaction: 2 histories processed.'),  # noqa: E501
                ('collective.revisionmanager.statscache', 'DEBUG', 'processing history 3'),  # noqa: E501
                ('collective.revisionmanager.statscache', 'DEBUG', 'processing history 4'),  # noqa: E501
                ('collective.revisionmanager.statscache', 'INFO', 'committing subtransaction: 4 histories processed.'))  # noqa: E501

    def test_stats_for_purged_revisions(self):
        """Stats calculation should work if all version of an object
        have been purged and there is no working copy
        """
        self.maxDiff = None
        cache = getUtility(IHistoryStatsCache)
        self.portal.portal_catalog.unindexObject(self.portal.obj)
        self.portal._delOb('obj')
        self.portal_storage.purge(1, 3, build_metadata('purged v4'))
        cache.refresh()
        self.portal_storage.purge(1, 2, build_metadata('purged v3'))
        cache.refresh()
        self.portal_storage.purge(1, 1, build_metadata('purged v2'))
        cache.refresh()
        self.portal_storage.purge(1, 0, build_metadata('purged v1'))
        cache.refresh()
        got = \
            [hist for hist in cache['histories'] if hist['history_id'] == 1][0]
        self.assertTrue(len(got['wcinfos']) == 1)
        wcinfo = got['wcinfos'][0]
        self.assertTrue(wcinfo['portal_type'] == '-')
        self.assertTrue(wcinfo['path'] == 'All revisions have been purged')

    def test_absolute_url_rewritten_by_proxy(self):
        """See
        https://github.com/collective/collective.revisionmanager/issues/8
        """
        cmf_uid = 999
        obj = CMFDummy('test_rewritten_url', cmf_uid)
        obj.text = 'test test'
        obj.allowedRolesAndUsers = ['Anonymous']
        self.portal._setObject('test_rewritten_url', obj)
        self.portal.portal_catalog.indexObject(self.portal.test_rewritten_url)
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj),
            metadata=build_metadata('saved v1'))
        obj.absolute_url = \
            lambda: 'http://staging.example.com/test_rewritten_url'
        cache = getUtility(IHistoryStatsCache)
        cache.refresh()


def mock_retrieve_pke(args):
    """Very specific decorator to make ZVCStorageTool.retrieve
    raise a POSKeyError if called with <args>.

    Maybe we could use some mock library for this ...
    """
    def decorate(m):
        def wrapped_m(*passedargs, **kwds):
            """So far <history_id> and <selector> are
            the only arguments to ZVCStorageTool.retrieve we are
            interested in. We expect them to be passed in as non kw
            args (looking at HistoryStatsCache._calculate_storage_statistics)
            """
            if passedargs == args and not kwds:
                raise POSKeyError('No blob file')
            return m(*passedargs, **kwds)
        wrapped_m.__name__ = m.__name__
        return wrapped_m
    return decorate


def mock_retrieve_pke_all_versions(args):
    """Another version of the above decorator
    that raises POSKeyError for all stored version
    """
    def decorate(m):
        def wrapped_m(*passedargs, **kwds):
            if passedargs[0] == args[0] and not kwds:
                raise POSKeyError('No blob file')
            return m(*passedargs, **kwds)
        wrapped_m.__name__ = m.__name__
        return wrapped_m
    return decorate


def mock_retrieve_with_brokenmodified(args):
    """Very specific decorator to make ZVCStorageTool.retrieve
    raise BrokenModified.
    """
    def decorate(m):
        def wrapped_m(*passedargs, **kwds):
            if passedargs == args and not kwds:
                raise BrokenModified("<persistent broken some.package.portlet.Assignment instance '\x00\x00\x00\x00\x00H\xf3\xc2'")  # noqa: E501
            return m(*passedargs, **kwds)
        wrapped_m.__name__ = m.__name__
        return wrapped_m
    return decorate


class POSKeyErrorTests(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.portal_storage = self.portal.portal_historiesstorage

        cmf_uid = 1
        obj1 = CMFDummy('obj', cmf_uid)
        obj1.text = 'v1 of text'
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj1),
            metadata=build_metadata('saved v1'))

        obj2 = CMFDummy('obj', cmf_uid)
        obj2.text = 'v2 of text'
        self.portal_storage.save(
            cmf_uid,
            ObjectData(obj2),
            metadata=build_metadata('saved v2'))

        obj3 = CMFDummy('obj', cmf_uid)
        obj3.text = 'v3 of text'
        self.portal_storage.save(
            cmf_uid,
            ObjectData(obj3),
            metadata=build_metadata('saved v3'))

    def test_retrieve_histories_with_poskeyerror_no_blob_file(self):
        """The histories storage might be inconsistent at times and
        retrieve() might raise POSKeyErrors. Test this case.
        """
        # decorate portal_historiesstorage retrieve method with mock
        self.portal_storage.retrieve = \
            mock_retrieve_pke((1,))(self.portal_storage.retrieve)
        cache = getUtility(IHistoryStatsCache)
        with LogCapture(
                'collective.revisionmanager.statscache', level=WARN) as log:
            cache.refresh()
            log.check(
                ('collective.revisionmanager.statscache', 'WARNING',
                 "POSKeyError encountered trying to retrieve history 1: 'No blob file'"),  # noqa: E501
            )
        expected = {
            'summaries': {
                'existing_versions': 0,
                'total_average': '3.0',
                'deleted_versions': 3,
                'existing_average': 'n/a',
                'total_versions': 3,
                'deleted_average': '3.0',
                'existing_histories': 0,
                'total_histories': 1,
                'deleted_histories': 1},
            'histories': [{
                'history_id': 1,
                'length': 3,
                'wcinfos': [{
                    'url': None,
                    'path': 'no working copy, object id: obj',
                    'portal_type': 'Dummy'}],
                'size_state': 'approximate'}]}
        got = cache
        for k, v in expected['summaries'].items():
            self.assertEqual(got['summaries'][k], v)
        # the time needed to calculate stats may vary
        self.assertLess(float(got['summaries']['time']), 1)
        self.assertEqual(len(expected['histories']), len(got['histories']))
        for idx in range(len(expected['histories'])):
            e = expected['histories'][idx]
            g = got['histories'][idx]
            for k, v in e.items():
                self.assertEqual(g[k], v)
            # The actual size is not important and we want robust tests,
            self.assertGreater(g['size'], 0)

    def test_working_copy_deleted_and_poskeyerror(self):
        """See
        https://github.com/collective/collective.revisionmanager/issues/9
        """
        cmf_uid = 2
        obj4 = CMFDummy('no_working_copy', cmf_uid)
        obj4.text = 'test the case when the working copy was deleted'
        self.portal._setObject('obj4', obj4)
        self.portal.portal_catalog.indexObject(self.portal.obj4)
        self.portal_storage.register(
            cmf_uid,
            ObjectData(obj4),
            metadata=build_metadata('v1'))
        self.portal.portal_catalog.unindexObject(self.portal.obj4)
        self.portal.manage_delObjects(['obj4'])
        self.portal_storage.retrieve = \
            mock_retrieve_pke_all_versions((2,))(self.portal_storage.retrieve)
        cache = getUtility(IHistoryStatsCache)
        with LogCapture(
                'collective.revisionmanager.statscache', level=WARN) as log:
            cache.refresh()
            log.check(
                ('collective.revisionmanager.statscache', 'WARNING',
                 "POSKeyError encountered trying to retrieve history 2: 'No blob file'"),  # noqa: E501
            )
        expected = [{
            'url': None,
            'path': 'POSKeyError encountered!',
            'portal_type': '-'}]
        got = [h for h in cache['histories'] if h['history_id'] == 2][0]['wcinfos']  # noqa: E501
        self.assertEqual(expected, got)

    def test_retrieve_histories_with_brokenmodified(self):
        """When a class is removed that a revision relies upon
        (e.g. when a revision of a document has a Assignment for a portlet
        that was removed later) BrokenModified is Raised.
        """
        # decorate portal_historiesstorage retrieve method with mock
        self.portal_storage.retrieve = mock_retrieve_with_brokenmodified((1,))(self.portal_storage.retrieve)  # noqa: E501
        cache = getUtility(IHistoryStatsCache)
        with LogCapture(
                'collective.revisionmanager.statscache', level=WARN) as log:
            cache.refresh()
            log.check(
                ('collective.revisionmanager.statscache', 'WARNING',
                 "BrokenModified encountered trying to retrieve history 1: <persistent broken some.package.portlet.Assignment instance '\x00\x00\x00\x00\x00H\xf3\xc2'"),  # noqa: E501
            )
        expected = {
            'summaries': {
                'existing_versions': 0,
                'total_average': '3.0',
                'deleted_versions': 3,
                'existing_average': 'n/a',
                'total_versions': 3,
                'deleted_average': '3.0',
                'existing_histories': 0,
                'total_histories': 1,
                'deleted_histories': 1},
            'histories': [{
                'history_id': 1,
                'length': 3,
                'wcinfos': [{
                    'url': None,
                    'path': 'no working copy, object id: obj',
                    'portal_type': 'Dummy'}],
                'size_state': 'approximate'}]}
        got = cache
        for k, v in expected['summaries'].items():
            self.assertEqual(got['summaries'][k], v)
        # the time needed to calculate stats may vary
        self.assertLess(float(got['summaries']['time']), 1)
        self.assertEqual(len(expected['histories']), len(got['histories']))
        for idx in range(len(expected['histories'])):
            e = expected['histories'][idx]
            g = got['histories'][idx]
            for k, v in e.items():
                self.assertEqual(g[k], v)
            # The actual size is not important and we want robust tests,
            self.assertGreater(g['size'], 0)
