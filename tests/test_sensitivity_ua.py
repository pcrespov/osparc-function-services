# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable


from typing import NamedTuple, Sequence

import numpy as np
import pytest
from osparc_function_services.sensitivity_ua import (
    MetropolisHastingsUncertainty,
    iter_sensitivity,
    linear_regression,
    myfunc,
    sensitivity,
    uncertainty,
)


@pytest.fixture
def myparamrefs():
    return [1, 2, 3]


@pytest.fixture
def myparamuncerts():
    return [0.1, 0.1, 0.5]


@pytest.fixture
def myparamuncerttypes():
    return ["N", "R", "N"]


@pytest.fixture
def diff_or_fact():
    return True


@pytest.fixture
def lin_or_power():
    return True


def test_1(
    myparamrefs, myparamuncerts, myparamuncerttypes, diff_or_fact, lin_or_power: bool
):

    sensitivity(myfunc, myparamrefs, myparamuncerts, diff_or_fact, lin_or_power)

    u = uncertainty(
        myfunc,
        myparamrefs,
        myparamuncerts,
        myparamuncerttypes,
        diff_or_fact,
        lin_or_power,
    )

    print("val:", u[0], "+-", u[2], "(", u[3], "dB)")
    print("uncertainty contributions:", u[1])
    print("sensitivity factors:", u[4])
    print("linearity:", u[5])


def test_2(myparamrefs, myparamuncerts, myparamuncerttypes, diff_or_fact):
    lin_or_power = False

    sensitivity(myfunc, myparamrefs, myparamuncerts, diff_or_fact, lin_or_power)
    u = uncertainty(
        myfunc,
        myparamrefs,
        myparamuncerts,
        myparamuncerttypes,
        diff_or_fact,
        lin_or_power,
    )

    print("val:", u[0], "+-", u[2], "(", u[3], "dB)")
    print("uncertainty contributions:", u[1])
    print("sensitivity factors:", u[4])
    print("linearity:", u[5])


def test_3(myparamrefs, myparamuncerttypes):

    myparamuncerts = [1.1, 1.05, 1.16]
    diff_or_fact = False
    lin_or_power = True

    sensitivity(myfunc, myparamrefs, myparamuncerts, diff_or_fact, lin_or_power)
    u = uncertainty(
        myfunc,
        myparamrefs,
        myparamuncerts,
        myparamuncerttypes,
        diff_or_fact,
        lin_or_power,
    )

    print("val:", u[0], "+-", u[2], "(", u[3], "dB)")
    print("uncertainty contributions:", u[1])
    print("sensitivity factors:", u[4])
    print("linearity:", u[5])


def test_4(myparamrefs, myparamuncerts, myparamuncerttypes, diff_or_fact):
    lin_or_power = False

    sensitivity(myfunc, myparamrefs, myparamuncerts, diff_or_fact, lin_or_power)
    u = uncertainty(
        myfunc,
        myparamrefs,
        myparamuncerts,
        myparamuncerttypes,
        diff_or_fact,
        lin_or_power,
    )

    print("val:", u[0], "+-", u[2], "(", u[3], "dB)")
    print("uncertainty contributions:", u[1])
    print("sensitivity factors:", u[4])
    print("linearity:", u[5])


def test_5(myparamrefs, myparamuncerts, myparamuncerttypes):
    nrruns = 10
    estimates = np.zeros((nrruns, 2))

    for i in range(nrruns):
        estimates[i, :] = MetropolisHastingsUncertainty(
            myfunc, myparamrefs, myparamuncerts, myparamuncerttypes, 20, 1000
        )

    print(
        "(",
        estimates[:, 0].mean(),
        "+-",
        estimates[:, 0].std(),
        ")",
        "+-",
        "(",
        estimates[:, 1].mean(),
        "+-",
        estimates[:, 1].std(),
        ")",
    )


def test_6(myparamrefs, myparamuncerts, myparamuncerttypes):
    nrruns = 10
    estimates = np.zeros((nrruns, 2))

    for i in range(nrruns):
        estimates[i, :] = MetropolisHastingsUncertainty(
            myfunc, myparamrefs, myparamuncerts, myparamuncerttypes, 1000, 10000
        )

    print(
        "(",
        estimates[:, 0].mean(),
        "+-",
        estimates[:, 0].std(),
        ")",
        "+-",
        "(",
        estimates[:, 1].mean(),
        "+-",
        estimates[:, 1].std(),
        ")",
    )


def test_7(myparamrefs, myparamuncerts, myparamuncerttypes):

    MetropolisHastingsUncertainty(
        myfunc, myparamrefs, myparamuncerts, myparamuncerttypes, 100, 100000
    )


# helper
class SensitivityReference(NamedTuple):
    refval: Sequence[float]
    sensitivites: Sequence[float]
    linearities: Sequence[float]


def test_sensitivity_meta_study_pipeline(
    myparamrefs,
    myparamuncerts,
    diff_or_fact: bool,
    lin_or_power: bool,
):
    r = sensitivity(myfunc, myparamrefs, myparamuncerts, diff_or_fact, lin_or_power)
    expected = SensitivityReference(*r)

    refval = myfunc(myparamrefs)

    for i, paramtestplus, paramtestminus in iter_sensitivity(
        paramrefs=myparamrefs, paramdiff=myparamuncerts, diff_or_fact=diff_or_fact
    ):

        testvalplus = myfunc(paramtestplus)
        testvalminus = myfunc(paramtestminus)

        refval0, sensitivity_i, linearity_i = linear_regression(
            i,
            paramrefs=myparamrefs,
            paramtestplus=paramtestplus,
            paramtestminus=paramtestminus,
            refval=refval,
            testvalplus=testvalplus,
            testvalminus=testvalminus,
            lin_or_power=lin_or_power,
        )

        assert refval == refval0
        assert expected.refval == refval0
        assert expected.sensitivites[i] == sensitivity_i
        assert expected.linearities[i] == linearity_i
