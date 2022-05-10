import time
from numbers import Complex
from typing import Tuple

from pydantic import BaseModel, Field

# Units validated against https://github.com/hgrecco/pint/blob/master/pint/default_en.txt


class Complex(BaseModel):
    real: float = Field(0.0, description="This is the real part")
    imag: float = Field(0.0, ge=0.0)


def demo_func(
    *, index: int, real_value: float, complex_value: Complex
) -> Tuple[int, float, Complex]:

    print("Sleeping 1.0")
    time.sleep(secs=1.0)

    return (index, real_value, complex_value)
