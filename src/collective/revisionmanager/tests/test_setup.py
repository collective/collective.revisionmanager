# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING  # noqa
from plone import api

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
        """Test that ICollectiveRevisionmanagerLayer is registered."""
        from collective.revisionmanager.interfaces import (
            ICollectiveRevisionmanagerLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveRevisionmanagerLayer, utils.registered_layers())


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
