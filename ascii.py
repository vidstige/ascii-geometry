from typing import List

import numpy as np

SIMPLE = b' .:-=+*#%@'
LONG = b' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'

def shade(buffer: np.array, sequence: str=SIMPLE) -> List[str]:
    eps = 0.00001
    lookup = ((buffer - eps) * len(sequence)).astype(np.int)
    return [bytes(sequence[i] for i in line) for line in lookup]
