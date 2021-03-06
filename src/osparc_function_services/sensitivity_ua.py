#!/usr/bin/env python
# coding: utf-8
#
# does it make sense to keep both diff_or_fact and lin_or_power?
# we could instead have a single dB option.
# code would be cleaner and there would not be asymmetry issues
#
import math
import random
from copy import deepcopy
from typing import Iterator, List, Sequence, Tuple

import numpy as np
from scipy.stats import norm, uniform
from sklearn.linear_model import LinearRegression


def sensitivity(func, paramrefs, paramdiff, diff_or_fact, lin_or_power):
    sensitivities = []
    linearities = []

    refval = func(paramrefs)

    if len(paramrefs) != len(paramdiff):
        return [refval, sensitivities, linearities]

    linear_regressor = LinearRegression()

    for i in range(len(paramrefs)):
        paramtestplus = paramrefs.copy()
        paramtestminus = paramrefs.copy()
        if diff_or_fact:
            paramtestplus[i] += paramdiff[i]
        else:
            paramtestplus[i] *= paramdiff[i]
        if diff_or_fact:
            paramtestminus[i] -= paramdiff[i]
        else:
            paramtestminus[i] /= paramdiff[i]  # check that not zero

        testvalplus = func(paramtestplus)

        testvalminus = func(paramtestminus)

        x = np.array([paramrefs[i], paramtestplus[i], paramtestminus[i]]).reshape(
            (-1, 1)
        )
        y = np.array([refval, testvalplus, testvalminus])
        if not lin_or_power:
            x = np.log(x / x[1])  # must be larger than zero
            y = np.log(y / y[1])
        model = linear_regressor.fit(x, y)
        sensitivities.append(model.coef_[0])
        linearities.append(model.score(x, y))

    return refval, sensitivities, linearities


def uncertainty(
    func, paramrefs, paramuncerts, paramuncerttypes, diff_or_fact, lin_or_power
):
    # this is run in osparc
    refval, sensitivities, linearities = sensitivity(
        func, paramrefs, paramuncerts, diff_or_fact, lin_or_power
    )

    uncerts = []

    totaluncert = 0.0
    totaluncertdB = 0.0

    if (len(paramrefs) != len(paramuncerts)) or (
        len(paramrefs) != len(paramuncerttypes)
    ):
        return refval, uncerts, totaluncert, totaluncertdB, sensitivities, linearities

    for i in range(len(paramrefs)):
        if lin_or_power:
            if diff_or_fact:
                uncerts.append(sensitivities[i] * paramuncerts[i])
            else:
                uncerts.append(
                    sensitivities[i] * paramrefs[i] * (paramuncerts[i] - 1)
                )  # not symmetric
        else:
            if diff_or_fact:
                uncerts.append(
                    sensitivities[i] * np.log(paramuncerts[i] / paramrefs[i] + 1)
                )  # not symmetric
            else:
                uncerts.append(sensitivities[i] * np.log(paramuncerts[i]))

        if paramuncerttypes[i] == "R":
            uncerts[i] /= math.sqrt(3)

        totaluncert += uncerts[i] ** 2
    totaluncert = math.sqrt(totaluncert)
    totaluncertdB = totaluncert
    if lin_or_power:
        totaluncertdB = np.log(totaluncert / refval + 1)  # not symmetric
    else:
        totaluncert = (np.exp(totaluncertdB) - 1) * refval  # not symmetric
    return refval, uncerts, totaluncert, totaluncertdB, sensitivities, linearities


def MetropolisHastingsUncertainty(
    func, paramrefs, paramuncerts, paramuncerttypes, initcount, totalcount
):  # diff_or_fact
    # https://en.wikipedia.org/wiki/Metropolis%E2%80%93Hastings_algorithm
    n = len(paramrefs)
    jumpfactor = 0.5
    alpha = 0.0
    valsum = 0.0
    val2sum = 0.0

    currentparams = paramrefs.copy()

    counter = 0
    while counter < totalcount:
        i = random.randrange(n)
        candidate = norm.rvs(currentparams[i], paramuncerts[i] * jumpfactor)

        if paramuncerttypes[i] == "R":
            alpha = uniform.pdf(
                candidate, paramrefs[i] - paramuncerts[i], 2 * paramuncerts[i]
            ) / uniform.pdf(
                currentparams[i], paramrefs[i] - paramuncerts[i], 2 * paramuncerts[i]
            )
        else:
            alpha = norm.pdf(candidate, paramrefs[i], paramuncerts[i]) / norm.pdf(
                currentparams[i], paramrefs[i], paramuncerts[i]
            )

        if uniform.rvs() < alpha:
            currentparams[i] = candidate

        if counter > initcount:
            val = func(currentparams)
            valsum += val
            val2sum += val**2

        counter += 1

    valmean = valsum / (totalcount - initcount)
    val2mean = val2sum / (totalcount - initcount)
    valstddev = math.sqrt(val2mean - valmean**2)

    return [valmean, valstddev]


def myfunc(x):
    prod = 1
    for i in x:
        prod *= i**2
    return prod


#
# Decomposing into service Kernels
#


def iter_sensitivity(
    *,
    paramrefs: List[float],
    paramdiff: List[float],
    diff_or_fact: bool,
) -> Iterator[Tuple[int, List[float], List[float]]]:

    assert len(paramrefs) == len(paramdiff)  # nosec

    n_dims = len(paramrefs)

    for i in range(n_dims):
        paramtestplus = deepcopy(paramrefs)
        paramtestminus = deepcopy(paramrefs)

        # inc/dec one dimension at a time
        if diff_or_fact:
            paramtestplus[i] += paramdiff[i]
        else:
            paramtestplus[i] *= paramdiff[i]

        if diff_or_fact:
            paramtestminus[i] -= paramdiff[i]
        else:
            paramtestminus[i] /= paramdiff[i]  # check that not zero

        yield (i, paramtestplus, paramtestminus)


def linear_regression(
    i: int,  # iteration index
    paramrefs: Sequence[float],
    paramtestplus: Sequence[float],
    paramtestminus: Sequence[float],
    refval: float,
    testvalplus: float,
    testvalminus: float,
    lin_or_power: bool,
):
    linear_regressor = LinearRegression()

    x = np.array([paramrefs[i], paramtestplus[i], paramtestminus[i]]).reshape((-1, 1))
    y = np.array([refval, testvalplus, testvalminus])
    if not lin_or_power:
        x = np.log(x / x[1])  # must be larger than zero
        y = np.log(y / y[1])

    model = linear_regressor.fit(x, y)
    sensitivity = model.coef_[0]
    linearity = model.score(x, y)

    return refval, sensitivity, linearity
