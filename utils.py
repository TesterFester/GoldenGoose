
def safe_get(obj, *keys, default=None):
    cur = obj
    for key in keys:
        if isinstance(cur, dict):
            cur = cur.get(key, default)
        elif isinstance(cur, list) and isinstance(key, int):
            if 0 <= key < len(cur):
                cur = cur[key]
            else:
                return default
        else:
            return default
        if cur is None:
            return default
    return cur

def first_valid_numeric(values, min_value=None, max_value=None):
    for v in values:
        try:
            x = float(v)
            if min_value is not None and x < min_value:
                continue
            if max_value is not None and x > max_value:
                continue
            return x
        except Exception:
            continue
    return None
