# -*- coding: utf-8 -*-
from collective.revisionmanager.interfaces import IHistoryStatsCache
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_FUNCTIONAL_TESTING  # noqa: E501
from collective.revisionmanager.testing import COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield.value import RichTextValue
from plone.testing.z2 import Browser
from zope.component import getUtility
from zope.lifecycleevent import modified

import six
import transaction
import unittest


class TestHistoriesView(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title=u'Some Document',
        )
        self.doc1.text = RichTextValue(u'One two', 'text/plain', 'text/html')
        modified(self.doc1)
        self.statscache = getUtility(IHistoryStatsCache)
        self.statscache.refresh()

    def test_view_displays_info_on_revisions(self):
        view = api.content.get_view(
            u'histories', self.portal, self.request)
        html = view()
        self.assertIn('<td>2 (0)</td>', html)
        if six.PY2:
            size = "3 kB"  # pragma: no cover
        else:
            size = "4 kB"
        self.assertIn('<td align="right">{}</td>'.format(size), html)
        self.assertIn(
            '<a href="http://nohost/plone/some-document">/some-document</a>',
            html)
        self.doc1.text = RichTextValue(u'Changed!', 'text/plain', 'text/html')
        modified(self.doc1)
        self.statscache.refresh()
        html = view()
        self.assertEqual(view.batch[0]['length'], 3)
        self.assertIn('<td>3 (0)</td>', html)
        if six.PY2:
            size = "5 kB"  # pragma: no cover
        else:
            size = "6 kB"
        self.assertIn('<td align="right">{}</td>'.format(size), html)

    def test_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@histories')

    def test_humanize(self):
        view = api.content.get_view(
            u'histories', self.portal, self.request)
        self.assertEqual(view.humanize_size(244), u'244 bytes')
        self.assertEqual(view.humanize_size(1), u'1 byte')
        self.assertEqual(view.humanize_size(None), u'0 bytes')
        self.assertEqual(view.humanize_size(6666666), u'6.4 MB')
        self.assertEqual(view.humanize_size(6666666666), u'6.21 GB')
        self.assertEqual(view.humanize_size(988772635482736), u'899.28 TB')


class TestViewsFunctional(unittest.TestCase):

    layer = COLLECTIVE_REVISIONMANAGER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title=u'Some Document',
        )
        self.doc1.text = RichTextValue(u'One two', 'text/plain', 'text/html')
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        modified(self.doc1)
        self.statscache = getUtility(IHistoryStatsCache)
        self.statscache.refresh()
        import transaction
        transaction.commit()
        # Set up browser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {}:{}'.format(TEST_USER_NAME, TEST_USER_PASSWORD)
        )

    def test_views_functional(self):
        self.browser.open(self.portal_url + '/@@revisions-controlpanel')
        self.browser.getControl(name='form.buttons.recalculate').click()
        self.browser.open(self.portal_url + '/@@histories')
        self.assertIn('<td>2 (0)</td>', self.browser.contents)
        if six.PY2:
            size = "3 kB"  # pragma: no cover
        else:
            size = "4 kB"
        self.assertIn('<td align="right">{}</td>'.format(size), self.browser.contents)
        self.doc1.text = RichTextValue(u'Changed!', 'text/plain', 'text/html')
        modified(self.doc1)
        # Refresh the cache.  Could also be done by clicking on the recalculate
        # button in the control panel, but this is easier:
        self.statscache.refresh()
        transaction.commit()
        self.browser.reload()
        # We have a item with 3 revisions
        self.assertIn('<td>3 (0)</td>', self.browser.contents)
        if six.PY2:
            size = "5 kB"  # pragma: no cover
        else:
            size = "6 kB"
        self.assertIn('<td align="right">{}</td>'.format(size), self.browser.contents)

        checkbox = self.browser.getControl(name='delete:list')
        self.assertEqual(checkbox.options, ['check1'])
        # TODO: Might need this on Plone 5.1 and earlier, or with Py 2.7:
        # checkbox.value = ['checked']
        checkbox.value = ['check1']
        # we keep a revision
        self.browser.getControl(name='keepnum').value = '2'
        self.browser.getControl(name='del_histories').click()
        # The size is not yet recalculated
        self.assertIn('<td align="right">???</td>', self.browser.contents)
        # Refresh the cache.
        self.statscache.refresh()
        transaction.commit()
        self.browser.open(self.portal_url + '/@@histories')

        # The number of revisions is kept but the payload is purged
        self.assertIn('<td>3 (1)</td>', self.browser.contents)
        # Now the size has been recalucated.
        self.assertNotIn('<td align="right">???</td>', self.browser.contents)
        # Remove all revisions.
        self.browser.getControl(name='keepnum').value = '0'
        self.browser.getControl(name='delete:list').value = ['check1']
        self.browser.getControl(name='del_histories').click()
        # No more items with revisions
        self.assertNotIn('name="delete:list"', self.browser.contents)

        # at least click the button even though there are no orphans
        self.browser.getControl(name='del_orphans').click()
