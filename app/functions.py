from ax.utils.measurement.synthetic_functions import hartmann6, aug_hartmann6
import numpy as np
from pydantic import BaseModel


class Hartmann6Inputs(BaseModel):
    x1: float
    x2: float
    x3: float
    x4: float
    x5: float
    x6: float

class AugHartmann6Inputs(Hartmann6Inputs):
    x7: float

class Hartmann6():
    def __init__(self):
        self.function_name = 'Hartmann6'

    def evaluate(self, x1, x2, x3, x4, x5, x6):
        x = np.array([x1, x2, x3, x4, x5, x6])
        return {"hartmann6": (hartmann6(x), 0.0), "l2norm": (np.sqrt((x**2).sum()), 0.0)}

class AugHartmann6():
    def __init__(self):
        self.function_name = 'AugHartmann6'

    def evaluate(self, x1, x2, x3, x4, x5, x6, x7):
        x = np.array([x1, x2, x3, x4, x5, x6, x7])
        return {"hartmann6": (aug_hartmann6(x), 0.0), "l2norm": (np.sqrt((x**2).sum()), 0.0)}