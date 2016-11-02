# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.browserlayer.utils import registered_layers

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.revisionmanager is properly installed."""

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.revisionmanager is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.revisionmanager'))

    def test_browserlayer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('ICollectiveRevisionmanagerLayer', layers)

    def test_persistent_utility(self):
        sm = self.portal.getSiteManager()
        self.assertIsNotNone(sm.getUtility(IHistoryStatsCache))


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.revisionmanager'])

    def test_product_uninstalled(self):
        """Test if collective.revisionmanager is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.revisionmanager'))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('ICollectiveRevisionmanagerLayer', layers)

    def test_persistent_utility_removed(self):
        from zope.component.interfaces import ComponentLookupError
        with self.assertRaises(ComponentLookupError):
            sm = self.portal.getSiteManager()
            sm.getUtility(IHistoryStatsCache)
