# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Int
from Products.CMFPlone import PloneMessageFactory as _


class ICollectiveRevisionmanagerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IHistoryStatsCache(Interface):
    """ caching statistics for portal_historiesstorage
    """

    def refresh():
        """ refresh the cache form portal_historiesstorage
        """


class IRevisionSettingsSchema(Interface):
    """ schema providing a unified interface for various CMFEditions
    - portal_purgepolicy (max number of versions to keep in storage)
    - ...
    """

    number_versions_to_keep = Int(
        title=_(u'number of versions to keep'),
        description=_(u'maximum number of versions to keep in the storage (set to -1 for infinite)'),  # noqa
        default=-1)
