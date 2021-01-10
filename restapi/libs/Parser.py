from typing import List

def parse_int_list(items: str, seperator: str) -> List[int]:
    try:
        return [int(float(item)) for item in items.split(seperator)]
    except Exception:
        return None

def parse_str_list(items: str, seperator: str) -> List[str]:
    try:
        return list(filter(None,[item for item in items.split(seperator)]))
    except Exception:
        return None
