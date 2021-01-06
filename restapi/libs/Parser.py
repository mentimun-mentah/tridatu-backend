from typing import List

def parse_int_list(items: List[str], seperator: str) -> List[int]:
    try:
        return [int(float(item)) for item in items.split(seperator)]
    except Exception:
        return None
