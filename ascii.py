import numpy as np


SIMPLE = b' .:-=+*#%@'

def shade(buffer: np.array, sequence: str=SIMPLE) -> np.chararray:
    eps = 0.00001
    lookup = ((buffer - eps) * len(sequence)).astype(np.int)
    return b'\n'.join(bytes(sequence[i] for i in line) for line in lookup)

#A = np.clip(np.random.rand(24, 80) + 0.3, 0, 1)
#print(shade(A))
