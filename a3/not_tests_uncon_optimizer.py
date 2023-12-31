"""
This script tests your uncon_optimizer on two easy problems:
- Slanted quadratic function
- Bean function

To run tests, put this file in the same folder as your `uncon_optimizer.py`, and run
$ python tests_uncon_optimizer.py

NOTE:
- For your report, you should test your optimizer on the slanted quadratic function and the n-dimensional Rosenbrock function. (Not the bean function)
- Your optimizer must pass these tests; otherwise, you'll lose significant points. The autograder will run the same tests.
- I set loose tolerance here, but the competition uses tight tolerance of |g|_infinity <= 1e-6.
- You don't need to understand or edit this script.
- Do not upload this script to autograder when submitting. Only upload `uncon_optimizer.py` and other Python files called by `uncon_optimizer.py`.
"""

import numpy as np
import unittest

# import your optimizer
from uncon_optimizer import uncon_optimizer

rosenbrock_dims = 2


def set_dims(dim):
    global rosenbrock_dims
    rosenbrock_dims = dim


class FunctionWrapperWithCounter():
    """
    Attach a function call counter to a user-defined function

    To use:
    --------------------------------------------------
    # instantiate
    func = FunctionWrapperWithCounter(user_defined_function)

    # call function
    func(x)

    # get function calls
    fcalls = func.get_fcalls()
    --------------------------------------------------
    """

    def __init__(self, func):
        self._func = func
        self._fcalls = 0   # initialize function call counter
        self._max_fcalls = 10000   # maximum iterations

    def __call__(self, x):
        """ calls the user-provided function and count the function calls"""
        self._fcalls += 1

        # kill and exit if the function calls reached the limit
        if self._fcalls >= self._max_fcalls:
            raise RuntimeError(
                'You reached the function call limit of ' + str(self._max_fcalls) + '. Exit.')

        return self._func(x)

    def get_fcalls(self):
        """ get function calls"""
        return self._fcalls


def slanted_quad(x):
    """
    Slanted quadratic function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    g : ndarray, shape (2,)
        objective gradient
    """

    beta = 1.5

    f = x[0]**2 + x[1]**2 - beta * x[0] * x[1]
    return f


def func_slanted_quad(x):
    """
    Slanted quadratic function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    """

    beta = 1.5

    f = x[0]**2 + x[1]**2 - beta * x[0] * x[1]

    g = np.zeros(2)
    g[0] = 2 * x[0] - beta * x[1]
    g[1] = 2 * x[1] - beta * x[0]

    return f, g


def bean(x):
    """
    Bean function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    """

    x1 = x[0]
    x2 = x[1]

    f = (1. - x1)**2 + (1. - x2)**2 + 0.5 * (2 * x2 - x1**2)**2

    return f


def func_bean(x):
    """
    Bean function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    g : ndarray, shape (2,)
        objective gradient
    """

    x1 = x[0]
    x2 = x[1]

    f = (1. - x1)**2 + (1. - x2)**2 + 0.5 * (2 * x2 - x1**2)**2

    g = np.zeros(2)
    g[0] = -2. * (1 - x1) - 2. * x1 * (2 * x2 - x1**2)
    g[1] = -2. * (1 - x2) + 2. * (2 * x2 - x1**2)

    return f, g


def rosenbrock(x):
    """
    Rosenbrock function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    """

    f = (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2
    return f


def func_rosenbrock(x):
    """
    Rosenbrock function from Appendix D of the book

    Parameters
    ----------
    x : ndarray, shape (2,)
        design variables

    Returns
    -------
    f : float
        function value
    g : ndarray, shape (2,)
        objective gradient
    """

    f = (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2
    g = [400*x[0]**3 - 400*x[0]*x[1] + 2*x[0] - 2, 200*(x[1] - x[0]**2)]
    return f, g


def func_rosenbrock_nd(x):
    """
    Rosenbrock function from Appendix D of the book
    Partial derivatives from https://math.stackexchange.com/questions/4464953/partial-derivatives-of-the-multidimensional-rosenbrock-function
    Also available at https://docs.scipy.org/doc/scipy/tutorial/optimize.html#broyden-fletcher-goldfarb-shanno-algorithm-method-bfgs

    Parameters
    ----------
    x : ndarray
        design variables

    Returns
    -------
    f : float
        function value
    g : ndarray
        objective gradient
    """
    n = len(x)
    f = 0
    for i in range(n - 1):
        f += 100*(x[i + 1] - x[i]**2)**2 + (1 - x[i])**2

    g = np.zeros(n)
    for i in range(n):
        if i == 0:  # no n-1 term
            g[i] = -400*x[i]*(x[i+1]-x[i]**2) + 2*(x[i]-1)
        elif i == n-1:  # no n+1 term
            g[i] = 200*(x[i]-x[i-1]**2)
        else:
            g[i] = -400*x[i]*(x[i+1]-x[i]**2) + 2 * \
                (x[i]-1) + 200*(x[i]-x[i-1]**2)

    return f, g


class TestsYouMustPass(unittest.TestCase):
    options = {}
    output = {}

    def set_options(self, options_in):
        self.options = options_in

    def get_output(self):
        return self.output

    def _run_actual_test(self, func_in, x0, xopt_ref, fopt_ref):
        # add function call counter to the function
        func = FunctionWrapperWithCounter(func_in)

        # run optimizaiton
        xopt, fopt, output = uncon_optimizer(
            func, x0, epsilon_g=1e-6, options=self.options)

        # check optimal x and f
        np.testing.assert_allclose(
            xopt, xopt_ref, rtol=0, atol=1e-3, err_msg='x_opt is wrong')
        np.testing.assert_allclose(
            fopt, fopt_ref, rtol=0, atol=1e-3, err_msg='f_opt is wrong')

        # check objective gradient at the optimized point
        # call original function to not increment the call counter
        _, gopt = func_in(xopt)
        gnorm = np.max(np.abs(gopt))
        self.assertTrue(
            gnorm <= 1e-5, msg='Norm of objective gradient at x_opt did not satisfy |g|_infinity < 1e-6')

        # check if alias is provided
        self.assertIn(
            'alias', output, msg='Could not get your alias from `output`. Make sure to set your alias as instructed in the template.')

        # get function calls
        print('fcalls =', func.get_fcalls())

        output["func_in"] = func_in.__name__
        self.output = output

    def test_slanted_quad(self):
        """Slanted quadratic function"""

        # optimal solution
        xopt_ref = np.zeros(2)
        fopt_ref = 0.

        # initial point
        x0 = np.array([0., 3.])

        # run test
        self._run_actual_test(func_slanted_quad, x0, xopt_ref, fopt_ref)

        print(
            '-----------------------------------------------------------------------------')
        print(
            '   Your optimizer successfully solved the slanted quadratic function problem.')
        print('-----------------------------------------------------------------------------\n')

    def test_bean(self):
        """Bean function"""

        # optimal solution
        xopt_ref = np.array([1.21341, 0.824123])
        fopt_ref = 0.09194

        # initial point
        x0 = np.array([0., 0.])

        # run test
        self._run_actual_test(func_bean, x0, xopt_ref, fopt_ref)

        print(
            '-----------------------------------------------------------------------------')
        print('   Your optimizer successfully solved the bean problem.')
        print('-----------------------------------------------------------------------------\n')

    def test_rosenbrock(self):
        """Rosenbrock function"""

        # optimal solution
        xopt_ref = np.ones(2)
        fopt_ref = 0.

        # initial point
        x0 = np.zeros(2)

        # run test
        self._run_actual_test(func_rosenbrock, x0, xopt_ref, fopt_ref)

        print(
            '-----------------------------------------------------------------------------')
        print(
            '   Your optimizer successfully solved the rosenbrock function problem.')
        print('-----------------------------------------------------------------------------\n')

    def test_rosenbrock_nd(self):
        """N dimensional Rosenbrock function"""

        # optimal solution
        xopt_ref = np.ones(rosenbrock_dims)
        fopt_ref = 0.

        # initial point
        x0 = np.zeros(rosenbrock_dims)

        # run test
        self._run_actual_test(func_rosenbrock_nd, x0, xopt_ref, fopt_ref)

        print(
            '-----------------------------------------------------------------------------')
        print(
            f'   Your optimizer successfully solved the {rosenbrock_dims} dimensional rosenbrock function problem.')
        print('-----------------------------------------------------------------------------\n')


# if __name__ == '__main__':
#     unittest.main()
