from typing import List, Tuple

from .sensitivity_ua import linear_regression, myfunc

# TODO:
# services = ServicesRegistry()


def sensitivity_ua_test_func(*, x: list[float]) -> float:
    return myfunc(x)


# @services.add(return_outputs=["refval", "sensitivity", "linearity"])
def sensitivity_ua_linear_regression(
    *,
    dimension_index: int,
    paramrefs: List[float],
    paramtestplus: List[float],
    paramtestminus: List[float],
    refval: float,
    testvalplus: float,
    testvalminus: float,
    lin_or_power: bool,
) -> Tuple[float, float, float]:
    refval, sensitivity, linearity = linear_regression(
        i=dimension_index,
        paramrefs=paramrefs,
        paramtestplus=paramtestplus,
        paramtestminus=paramtestminus,
        refval=refval,
        testvalplus=testvalplus,
        testvalminus=testvalminus,
        lin_or_power=lin_or_power,
    )
    return refval, sensitivity, linearity
