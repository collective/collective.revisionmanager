from zope.component import getUtility
from .interfaces import IHistoryStatsCache

def clear_cache(context):
    cache = getUtility(IHistoryStatsCache)
    cache.clear()
