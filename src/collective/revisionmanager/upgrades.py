# -*- coding: utf-8 -*-
from .interfaces import IHistoryStatsCache
from zope.component import getUtility


def clear_cache(context):
    cache = getUtility(IHistoryStatsCache)
    cache.clear()
