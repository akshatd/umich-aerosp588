import numpy as np
import math
from matplotlib import pyplot as plt
from matplotlib import patches

from copy import deepcopy


class SimplexNode:
    def __init__(self, x, fx) -> None:
        self.x = x
        self.fx = fx

    def __repr__(self) -> str:
        return f'{self.x}\t{self.fx: .13f}'

    def set(self, x, fx) -> None:
        self.x = x
        self.fx = fx


def delta_x(simplex) -> float:
    """
    Calculate the sum of Euclidean distances between the points in a simplex.

    Args:
    simplex (list): List of points representing the simplex.

    Returns:
    float: The sum of Euclidean distances between the points in the simplex.
    """
    delta = 0
    for i in range(len(simplex)-1):
        delta += np.linalg.norm(simplex[i].x - simplex[-1].x)
    return delta


def delta_f(simplex) -> float:
    """
    Calculate the standard deviation of the function values in a simplex.

    Args:
    simplex (list): A list of function values in the simplex.

    Returns:
    float: The standard deviation of the function values.
    """
    return np.std(np.array([node.fx for node in simplex]))


def range_f(simplex) -> float:
    """
    Calculate the range of function values in a simplex.

    Args:
    simplex (list): A list of function values in the simplex.

    Returns:
    float: The range of the function values.
    """
    fxarray = np.array([node.fx for node in simplex])
    return np.max(fxarray) - np.min(fxarray)


def nelder_mead(f, guess, l=1, tau_x=1e-6, tau_f=1e-6, max_iter=100):
    """
    Nelder-Mead algorithm for finding the minimum of a function.

    Args:
      f: The function to minimize.
      guess: The initial guess for the minimum.
      l: edge length of the simplex
      tau_x: tolerance for change in x
      tau_f: tolerance for change in f
      max_iter: The maximum number of iterations to run the algorithm.

    Returns:
      An output dictionary with all the simplexes and the iterations taken.
    """

    # Create a simplex with edge length l
    n = len(guess)
    x0 = SimplexNode(guess, f(guess))
    sqrt2 = math.sqrt(2)
    sqrtnpl1 = math.sqrt(n+1)
    simplex = [x0]

    for j in range(n):
        # s(j) given by Eq. 7.2
        node_x = np.array(guess) + (l/(n*sqrt2)) * (sqrtnpl1-1)
        node_x[j] += (l/sqrt2)
        simplex.append(SimplexNode(node_x, f(node_x)))

    simplex_list = [np.array(deepcopy(simplex))]
    iters = 0
    # Iterate until the maximum number of iterations is reached or the simplex is sufficiently small.
    # Simplex size (Eq. 7.6) and standard deviation (Eq. 7.7)
    while iters < max_iter and (delta_x(simplex) > tau_x or delta_f(simplex) > tau_f):
        # Order from the lowest (best) to the highest f(x)
        simplex.sort(key=lambda node: node.fx)

        # The centroid excluding the worst point simplex[n] (Eq. 7.4)
        xc = np.mean([node.x for node in simplex[:-1]], axis=0)

        # Reﬂection, Eq. 7.3 with 𝛼 = 1
        xr = xc + (xc - simplex[-1].x)

        # Is reﬂected point is better than the best?
        fxr = f(xr)
        if fxr < simplex[0].fx:
            # Expansion, Eq. 7.3 with 𝛼 = 2
            xe = xc + 2 * (xc - simplex[-1].x)
            # Is expanded point better than the best?
            fxe = f(xe)
            if fxe < simplex[0].fx:
                # Accept expansion and replace worst point
                simplex[-1].set(xe, fxe)
            else:
                # Accept reﬂection
                simplex[-1].set(xr, fxr)

        # Is reﬂected better than second worst?
        elif fxr <= simplex[-2].fx:
            # Accept reﬂected point
            simplex[-1].set(xr, fxr)

        else:
            # Is reﬂected point worse than the worst?
            if fxr > simplex[-1].fx:
                # Inside contraction, Eq. 7.3 with 𝛼 = −0.5
                xic = xc - 0.5 * (xc - simplex[-1].x)
                # Inside contraction better than worst?
                fxic = f(xic)
                if fxic < simplex[-1].fx:
                    # Accept inside contraction
                    simplex[-1].set(xic, fxic)
                else:
                    # Shrink, Eq. 7.5 with 𝛾 = 0.5
                    for j in range(1, len(simplex)):
                        node_x = simplex[0].x + 0.5 * \
                            (simplex[j].x - simplex[0].x)
                        simplex[j].set(node_x, f(node_x))
            else:
                # Outside contraction, Eq. 7.3 with 𝛼 = 0.5
                xoc = xc + 0.5 * (xc - simplex[-1].x)
                # Is contraction better than reﬂection?
                fxoc = f(xoc)
                if fxoc < f(xr):
                    # Accept outside contraction
                    simplex[-1].set(xoc, fxoc)
                else:
                    # Shrink, Eq. 7.5 with 𝛾
                    for j in range(1, len(simplex)):
                        node = simplex[0].x + 0.5 * \
                            (simplex[j].x - simplex[0].x)
                        simplex[j].set(node, f(node))

        iters += 1
        simplex_list.append(np.array(deepcopy(simplex)))

    # Return the output
    output = {
        'simplex': np.array(simplex_list),
        'iters': iters,
        'success': iters < max_iter
    }
    return output


def plot_nm(f, simplex_list, title):
    """
    Plot the Nelder-Mead optimization algorithm progress.

    Args:
        f (function): The objective function to be optimized.
        simplex_list (list): List of simplices representing the progress of the Nelder-Mead algorithm.
        title (str): The title of the plot.

    Returns:
        None
    """

    # 2D simplex, so 3 points per item
    assert (simplex_list[0].shape[0] == 3)

    # get min and max for plotting
    x_list = []
    for simplex in simplex_list:
        x_list += ([node.x for node in simplex])
    x1_min, x2_min = np.min(x_list, axis=0)
    x1_max, x2_max = np.max(x_list, axis=0)

    # prep data for contours
    spread = 1
    x1 = np.linspace(x1_min-spread, x1_max+spread, 1000)
    x2 = np.linspace(x2_min-spread, x2_max+spread, 1000)
    x1, x2 = np.meshgrid(x1, x2)
    data = f([x1, x2])

    _, ax = plt.subplots()
    levels = np.linspace(np.min(data), np.max(data), 30)
    ax.contour(x1, x2, data, levels=levels)

    # annotate starting and optimal x
    x0 = (simplex_list[0][0].x[0], simplex_list[0][0].x[1])
    ax.annotate("x0", xy=x0, xytext=(x0[0]-0.2, x0[1]-0.2), color='red')

    xopt = (simplex_list[-1][0].x[0], simplex_list[-1][0].x[1])
    ax.annotate("x*", xy=xopt, xytext=(xopt[0]+0.2, xopt[1]+0.2), color='red')

    # add simplex triangles
    for simplex in simplex_list:
        ax.add_patch(patches.Polygon(
            [node.x for node in simplex], edgecolor='red', fill=False))

    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    plt.title(f'{title}')
    plt.show()


def plot_nm_bfgs(f, simplex_list, bfgs_progress, title):
    """
    Plot the Nelder-Mead and BFGS optimization algorithm progress.

    Args:
        f (function): The objective function to be optimized.
        simplex_list (list): List of simplices representing the progress of the Nelder-Mead algorithm.
        title (str): The title of the plot.

    Returns:
        None
    """

    # 2D simplex, so 3 points per item
    assert (simplex_list[0].shape[0] == 3)

    # get min and max for plotting
    x_list = []
    for simplex in simplex_list:
        x_list += ([node.x for node in simplex])
    x1_min, x2_min = np.min(x_list, axis=0)
    x1_max, x2_max = np.max(x_list, axis=0)

    # prep data for contours
    spread = 1
    x1 = np.linspace(x1_min-spread, x1_max+spread, 1000)
    x2 = np.linspace(x2_min-spread, x2_max+spread, 1000)
    x1, x2 = np.meshgrid(x1, x2)
    data = f([x1, x2])

    _, ax = plt.subplots()
    levels = np.linspace(np.min(data), np.max(data), 30)
    ax.contour(x1, x2, data, levels=levels)

    # annotate starting and optimal x
    x0 = (simplex_list[0][0].x[0], simplex_list[0][0].x[1])
    ax.annotate("x0", xy=x0, xytext=(x0[0]-0.2, x0[1]-0.2), color='red')

    xopt = (simplex_list[-1][0].x[0], simplex_list[-1][0].x[1])
    ax.annotate("x*", xy=xopt, xytext=(xopt[0]+0.2, xopt[1]+0.2), color='red')

    # add simplex triangles
    putlabel = True
    for simplex in simplex_list:
        if putlabel:
            ax.add_patch(patches.Polygon(
                [node.x for node in simplex], edgecolor='red', fill=False, label='Nelder-Mead'))
            putlabel = False
        else:
            ax.add_patch(patches.Polygon(
                [node.x for node in simplex], edgecolor='red', fill=False))

    # add BFGS progress
    x, y = np.array(bfgs_progress).T
    ax.plot(x, y, '-o', label='BFGS')
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.legend()
    plt.title(f'{title}')
    plt.show()
