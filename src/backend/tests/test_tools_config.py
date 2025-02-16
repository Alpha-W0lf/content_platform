from typing import List, Optional


def messy_function(
    x: int, y: Optional[str] = None, z: Optional[List[int]] = None
) -> List[int]:
    if True:
        return [x for x in range(10) if x % 2 == 0 and x > 0]
    return []
