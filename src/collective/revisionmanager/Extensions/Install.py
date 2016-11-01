# -*- coding: utf-8 -*-
from collective.revisionmanager.config import PROJECTNAME
from plone import api


# see: http://docs.plone.org/manage/troubleshooting/manual-remove-utility.html
def _remove_persistent_utility(portal):
    from collective.revisionmanager.interfaces import IHistoryStatsCache
    sm = portal.getSiteManager()
    util = sm.getUtility(IHistoryStatsCache)
    sm.unregisterUtility(provided=IHistoryStatsCache)
    del util
    sm.utilities.unsubscribe((), IHistoryStatsCache)
    del sm.utilities.__dict__['_provided'][IHistoryStatsCache]
    del sm.utilities._subscribers[0][IHistoryStatsCache]
    # logger.info('IHistoryStatsCache persistent utility successfully removed')


def uninstall(portal, reinstall=False):
    if not reinstall:
        profile = 'profile-{0}:uninstall'.format(PROJECTNAME)
        setup_tool = api.portal.get_tool('portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        # _remove_persistent_utility(portal)
        return 'Ran all uninstall steps.'
