from django.core.cache import cache

def book__cache(cache_key, queryset, timeout=100):
    """
    Caches the result of a queryset if not already cached.
    Returns:
        list: The cached queryset result.
    """
    if cache_key in cache:
        return cache.get(cache_key)
    else:
        queryset = queryset()
        cache.set(cache_key, list(queryset), timeout=timeout)
        return queryset
    
    
def top_book_cache(cache_key,queryset_fun,timeout=60*60*2):
    if cache_key in cache:
        return cache.get(cache_key)
    queryset=queryset_fun()
    cache.set(cache_key,list(queryset),timeout=timeout)
    return queryset



