import time

_values = {}

def get(key):
    item = _values.get(key)
    if not item or item[0] <= time.monotonic():
        _values.pop(key, None)
        return None
    return item[1]

def set_value(key, value, ttl_seconds=60):
    _values[key] = (time.monotonic() + ttl_seconds, value)
    return value

def clear():
    _values.clear()
