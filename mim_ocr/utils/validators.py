import numpy as np


def isnan(x) -> bool:
    """checks if dataframe value is nan or None.
    Takes into account different possibilities (e.g np.nan, float('NaN'))"""
    return x is np.nan or x != x or x is None
