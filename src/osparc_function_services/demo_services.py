import time
from enum import Enum
from numbers import Complex
from typing import Tuple

from pydantic import BaseModel, Field, confloat, conint, constr


class Complex(BaseModel):
    real: float = Field(0.0, description="This is the real part")
    imag: float = Field(0.0, ge=0.0)


class Answers(str, Enum):
    YES = "YES"
    NO = "NO"


def demo_func(
    *,
    index: conint(ge=1),
    real_value: confloat(multiple_of=2),
    string_value: constr(min_length=3),
    list_of_numbers: list[confloat(ge=0)],
    flag: bool = False,
    answer: Answers = "NO",
    complex_value: Complex,
) -> Tuple[int, float, bool]:

    # Some fake implementation
    print("Inputs")
    print(f"{index=}")
    print(f"{real_value=}")
    print(f"{string_value=}")
    print(f"{list_of_numbers=}")
    print(f"{flag=}")

    print("sleep 1.0")
    time.sleep(secs=1.0)
    print("Done")

    return (index, real_value, flag)
