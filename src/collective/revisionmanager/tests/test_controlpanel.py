# -*- coding: utf-8 -*-
from collective.revisionmanager.config import PROJECTNAME
from collective.revisionmanager.interfaces import IRevisionSettingsSchema
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


has_get_installer = True


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # pragma: no cover
    has_get_installer = False


class ControlPanelTestCase(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']

    def test_controlpanel_has_view(self):
        request = self.layer['request']
        view = api.content.get_view(
            u'revisions-controlpanel', self.portal, request)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@revisions-controlpanel')

    def test_controlpanel_installed(self):
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertIn('RevisionsControlPanel', actions)

    @unittest.skipIf(api.env.plone_version() < '5.0', 'FIXME')
    def test_controlpanel_removed_on_uninstall(self):
        with api.env.adopt_roles(['Manager']):
            if has_get_installer:
                installer = get_installer(self.portal)
                installer.uninstall_product(PROJECTNAME)
            else:  # pragma: no cover
                installer = api.portal.get_tool('portal_quickinstaller')
                installer.uninstallProducts(products=[PROJECTNAME])

        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertNotIn('RevisionsControlPanel', actions)


class RegistryTestCase(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IRevisionSettingsSchema)

    def test_number_versions_to_keep_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'number_versions_to_keep'))
        self.assertEqual(self.settings.number_versions_to_keep, -1)

    def test_subtransaction_threshold_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'subtransaction_threshold'))
        self.assertEqual(self.settings.subtransaction_threshold, 0)

    def test_records_removed_on_uninstall(self):
        with api.env.adopt_roles(['Manager']):
            if has_get_installer:
                installer = get_installer(self.portal)
                installer.uninstall_product(PROJECTNAME)
            else:  # pragma: no cover
                installer = api.portal.get_tool('portal_quickinstaller')
                installer.uninstallProducts(products=[PROJECTNAME])

        records = [
            IRevisionSettingsSchema.__identifier__ + '.number_versions_to_keep',  # noqa: E501
            IRevisionSettingsSchema.__identifier__ + '.subtransaction_threshold',  # noqa: E501
        ]

        for r in records:
            self.assertNotIn(r, self.registry)
