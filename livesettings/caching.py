from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

__all__ = ('USE_KEYEDCACHE', 'cache_key', 'cache_get', 'cache_set', 'NotCachedError', 'CachedObjectMixin')

USE_KEYEDCACHE = getattr(settings, 'LIVESETTINGS_USE_KEYEDCACHE', True)
if USE_KEYEDCACHE:
    try:
        import keyedcache
    except ImportError, e:
        raise ImproperlyConfigured("LIVESETTINGS_USE_KEYEDCACHE is %r but couldn't import keyedcache: %r" % (
            USE_KEYEDCACHE, e
        ))
    
    from keyedcache import cache_key, cache_get, cache_set, NotCachedError
    from keyedcache.models import CachedObjectMixin
else:
    # provide the same API as keyedcache but skip the middleman and just
    # defer directly to the django cache backend.
    
    class NotCachedError(Exception):
        pass
    
    def cache_key(*args):
        return ':'.join([unicode(val) for val in args])
    
    def cache_get(key):
        val = cache.get(key)
        if val is None:
            raise NotCachedError(key)
        return val
    
    def cache_set(key, value):
        cache.set(key, value, getattr(settings, 'CACHE_TIMEOUT', 300))
    
    def cache_delete(key):
        cache.delete(key)
    
    class CachedObjectMixin(object):
        def cache_delete(self, *args, **kwargs):
            key = self.cache_key(*args, **kwargs)
            cache_delete(key)
    
        def cache_get(self, *args, **kwargs):
            key = self.cache_key(*args, **kwargs)
            return cache.get(key)
    
        def cache_key(self, *args, **kwargs):
            keys = [self.__class__.__name__, self]
            keys.extend(args)
            return cache_key(*keys)
        
        def cache_reset(self):
            self.cache_delete()
            self.cache_set()
        
        def cache_set(self, *args, **kwargs):
            val = kwargs.pop('value', self)
            key = self.cache_key(*args, **kwargs)
            cache_set(key, value=val)
        
        def is_cached(self, *args, **kwargs):
            return self.cache_get(*args, **kwargs) is not None
