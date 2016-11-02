# -*- coding: utf-8 -*-
import logging
from plone import api
from Products.ZCatalog.ProgressHandler import ZLogHandler

log = logging.getLogger(__name__)


def post_install(context):
    """Post install script"""
    if context.readDataFile('collectiverevisionmanager_default.txt') is None:
        return
    catalog = api.portal.get_tool('portal_catalog')
    if 'cmf_uid' in catalog.indexes():
        return
    log.info('Adding cmf_uid catalog index')
    catalog.addIndex('cmf_uid', 'FieldIndex')
    log.info('Indexing cmf_uid index')
    pgthreshold = catalog._getProgressThreshold() or 100
    pghandler = ZLogHandler(pgthreshold)
    catalog.reindexIndex('cmf_uid', None, pghandler=pghandler)
    log.info('Finished indexing cmf_uid')
