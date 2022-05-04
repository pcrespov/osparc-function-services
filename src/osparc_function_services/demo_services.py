from numbers import Complex
from pydantic import BaseModel
from typing import Tuple
import time


class Complex(BaseModel):
    real: float = 0.0
    imag: float = 0.0




def demo_func(*, index: int, real_value: float, complex_value: Complex) -> Tuple[int, float, Complex]:
    print("Sleeping 1.0")
    time.sleep(secs=1.0)

    return (index, real_value, complex_value)
