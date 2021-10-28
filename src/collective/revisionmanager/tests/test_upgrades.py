# -*- coding: utf-8 -*-
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING
from collective.revisionmanager.upgrades import clear_cache
from plone import api
from zope.component import getUtility
from zope.location.interfaces import LocationError

import unittest


class UpgradeTo1001Tests(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_clear_cache(self):
        cache = getUtility(IHistoryStatsCache)
        self.assertTrue(len(cache) == 0)
        cache.refresh()
        # there's a typo in earlier versions, simulate it
        cache['summaries']['exisisting_histories'] = \
            cache['summaries']['existing_histories']
        del cache['summaries']['existing_histories']
        view = api.content.get_view(
            u'revisions-controlpanel', self.portal, self.request)
        self.assertRaises(LocationError, view)
        # now run the upgrade
        clear_cache(self.portal)
        self.assertTrue(len(cache) == 0)
        # the configlet should be accessible after the upgrade step
        self.assertTrue(view())
