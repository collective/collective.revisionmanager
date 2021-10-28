# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.browserlayer.utils import registered_layers

import unittest


has_get_installer = True


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # pragma: no cover
    has_get_installer = False


class TestSetup(unittest.TestCase):
    """Test that collective.revisionmanager is properly installed."""

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if has_get_installer:
            self.installer = get_installer(self.portal)
        else:  # pragma: no cover
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.revisionmanager is installed."""
        try:
            is_installed = self.installer.is_product_installed(
                'collective.revisionmanager')
        except AttributeError:  # pragma: no cover
            is_installed = self.installer.isProductInstalled(
                'collective.revisionmanager')
        self.assertTrue(is_installed)

    def test_browserlayer(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertIn('ICollectiveRevisionmanagerLayer', layers)

    def test_persistent_utility(self):
        sm = self.portal.getSiteManager()
        self.assertIsNotNone(sm.getUtility(IHistoryStatsCache))


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if has_get_installer:
            self.installer = get_installer(self.portal)
            self.installer.uninstall_product('collective.revisionmanager')
        else:  # pragma: no cover
            self.installer = api.portal.get_tool('portal_quickinstaller')
            self.installer.uninstallProducts(['collective.revisionmanager'])

    def test_product_uninstalled(self):
        """Test if collective.revisionmanager is cleanly uninstalled."""
        try:
            is_installed = self.installer.is_product_installed(
                'collective.revisionmanager')
        except AttributeError:  # pragma: no cover
            is_installed = self.installer.isProductInstalled(
                'collective.revisionmanager')
        self.assertFalse(is_installed)

    def test_addon_layer_removed(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertNotIn('ICollectiveRevisionmanagerLayer', layers)

    def test_persistent_utility_removed(self):
        try:
            from zope.interface.interfaces import ComponentLookupError
        except ImportError:  # pragma: no cover
            # Plone 4.3
            from zope.component.interfaces import ComponentLookupError
        with self.assertRaises(ComponentLookupError):
            sm = self.portal.getSiteManager()
            sm.getUtility(IHistoryStatsCache)
