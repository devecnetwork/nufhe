import time

import pytest
import numpy

from tfhe.numeric_functions import Torus32, Int32
from tfhe.polynomials_gpu import ShiftTorusPolynomial
from tfhe.polynomials_cpu import ShiftTorusPolynomialReference

from utils import get_test_array


@pytest.mark.parametrize('option', ['minus_one', 'invert_powers', 'powers_view'])
def test_shift_torus_polynomial(thread, option):

    polynomial_degree = 16
    shape = (20, 30)

    powers_shape = (20, 10) if option == 'powers_view' else (20,)
    powers_idx = 5 # not used unless `option == 'powers_view'`

    source = get_test_array(shape + (polynomial_degree,), Torus32)
    powers = get_test_array(powers_shape, Int32, (0, 2 * polynomial_degree))

    result = numpy.empty_like(source)

    source_dev = thread.to_device(source)
    powers_dev = thread.to_device(powers)
    result_dev = thread.empty_like(result)

    options = {option: True}

    comp = ShiftTorusPolynomial(polynomial_degree, shape, powers_shape, **options).compile(thread)
    ref = ShiftTorusPolynomialReference(polynomial_degree, shape, powers_shape, **options)

    comp(result_dev, source_dev, powers_dev, powers_idx)
    result_test = result_dev.get()

    ref(result, source, powers, powers_idx)

    assert numpy.allclose(result_test, result)
