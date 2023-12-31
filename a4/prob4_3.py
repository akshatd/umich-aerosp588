#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import check_grad, minimize

from uncon_optimizer import uncon_optimizer
import functions as fn


def plot_constrained_opt(fx, constr1, opt, title):
    plot_spread = 3
    # def plot_constrained_opt(fx, opt, title):
    x1, x2 = opt
    range_x1 = np.linspace(x1-plot_spread, x1+plot_spread, 1000)
    range_x2 = np.linspace(x2-plot_spread, x2+plot_spread, 1000)
    mesh_x1, mesh_x2 = np.meshgrid(range_x1, range_x2)
    data = fx([mesh_x1, mesh_x2])
    data_constr1 = constr1([mesh_x1, mesh_x2])
    _, ax = plt.subplots()
    levels = np.linspace(np.min(data), np.max(data), 30)
    ax.contour(mesh_x1, mesh_x2, data, levels=levels)
    # ax.contour(mesh_x1, mesh_x2, data)
    # ax.contourf(
    #     mesh_x1, mesh_x2, data_constr1, levels=[0, 22263044], colors='r')
    # ax.contour(mesh_x1, mesh_x2, data_constr1, levels=[0], colors='k')

    ax.plot(x1, x2, '-o')
    ax.annotate("optimum", xy=(x1, x2))
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    plt.title(f'{title}')
    plt.show()


# all the funcs must provide gradient!

# uh = equality penalty parameter
# ug = inequality penalty parameter

def pen_ext_quad(x, ug, f, df, g, dg):
    fx = f(x)
    gx = g(x)
    gx = np.where(gx > 0, gx, 0)
    gx_pen = ug/2 * np.sum(gx**2)

    dfx = df(x)
    # :, None to broadcast so that we can multiply element wise
    # axis=0 so all the x1s and x2s are added together
    dgx_pen = ug * np.sum(gx[:, None] * dg(x), axis=0)

    return fx+gx_pen, dfx+dgx_pen


def pen_int(x, ug, f, df, g, dg):
    fx = f(x)
    gx = g(x)
    gx_pen = ug * np.sum(np.log(-gx))
    dfx = df(x)
    dgx_pen = ug * np.sum(dg(x)/gx[:, None], axis=0)
    return fx-gx_pen, dfx-dgx_pen


h = .25
b = .125
sigma_yield = 200000000
tau_yeild = 116000000
P = 100000
l = 1


def I(x):
    return (3*x[0] + 16*x[0]**3 + x[1])/768


def can_constraint1(x):
    return P*l*h/(2*I(x))/sigma_yield - 1


def can_constraint2(x):
    return 1.5*P/(h*x[1])/tau_yeild - 1


def constraint_can(x):
    return can_constraint1(x) + can_constraint2(x)


# def pen_ext_quad_can(x, ug):
    # fx = 2*b*x[0] + h*x[1]
    # d_fx = np.array([2*b, h])
    # gfx = ug/2*max(0, can_constraint1(x))**2 + \
    #     ug/2*max(0, can_constraint2(x))**2
    # d_gfx = np.zeros(2)
    # d_gfx[0] = - 1152*can.h*can.l*can.P*ug*(16*x[0]**2 + 1)*(384*can.h*can.l*can.P-can.sigma_yield*(
    #     3*x[0] + 16*x[0]**3 + x[1]))/(3*x[0] + 16*x[0]**3 + x[1])**3
    # d_gfx[1] = - 384*can.P*can.l*can.h/(3*x[0] + 16*x[0]**3 + x[1])**3
    # d_gfx[0] += 0
    # d_gfx[1] += 1.5*can.P*ug * \
    #     (can.h*can.tau_yeild*x[1] - 1.5*can.P)/(can.h**2*x[1]**3)
    # return fx+gfx, d_fx+d_gfx
    # return 0, 0


# def pen_int_cant(x, ug):
#     return


class ConstrainedProblem:
    def __init__(self, f, df, h=None, dh=None, g=None, dg=None) -> None:
        self.f = f
        self.df = df
        self.h = h
        self.dh = dh
        self.g = g
        self.dg = dg


def penalized(pen_type, x, ug, problem: ConstrainedProblem):
    if pen_type == 'int':
        return lambda x: pen_int(x, ug, problem.f, problem.df, problem.g, problem.dg)
    elif pen_type == 'ext':
        return lambda x: pen_ext_quad(x, ug, problem.f, problem.df, problem.g, problem.dg)


def con_optimizer(problem: ConstrainedProblem, x0, epsilon_g, options=None, opt_options=None):
    if options is None:
        options = {}

    if "uh" not in options:
        options["uh"] = 1
    if "ug" not in options:
        options["ug"] = 1
    if "p" not in options:
        options["p"] = 2
    if "pen" not in options:
        options["pen"] = "ext"

    it = 0
    guess = x0
    guess_prev = guess

    uh = options['uh']
    ug = options['ug']

    # lists to keep track of function values
    guesses = [guess]
    if opt_options is None:
        opt_options = {}
        opt_options = {
            'step_init': 0.5,
        }
    constraints = problem.g
    constr_dist = np.sum(np.abs(constraints(guess)))
    constr_dists = [constr_dist]

    while constr_dist > epsilon_g:
        func_pen = penalized(options['pen'], guess, ug, problem)
        # print(
        #     f"Constrained Optimizer loop {it} with u:{ug}, guess: {guess}, f: {func_pen(guess)}, constraint dist: {constr_dist}")
        guess, f, output = uncon_optimizer(
            func_pen, guess_prev, epsilon_g, opt_options)
        guesses.append(guess)
        constr_dist = np.sum(np.abs(constraints(guess)))
        constr_dists.append(constr_dist)
        uh = options["p"]*uh
        ug = options["p"]*ug
        guess_prev = guess
        it += 1
    return guess


if __name__ == "__main__":
    print("- Exaple 5.4:")
    x0 = np.array([-2, -1])
    # x0 = np.array([-2, -2])
    # x0 = np.array([2, 1])
    # x0 = np.array([2, 2])
    e5_4 = ConstrainedProblem(fn.e5_4_f, fn.e5_4_df,
                              g=fn.e5_4_g, dg=fn.e5_4_dg)
    epsilon_g = 1e-5
    options = {
        'pen': 'ext',
        'uh': 1,
        'ug': 0.5,
        'p': 1.8,
    }
    opt_options = {
        'step_init': 1,
        'constraint': fn.e5_4_g
    }

    print(
        f"Exterior penalty: {(con_optimizer(e5_4, x0, epsilon_g, options, opt_options))}")

    x0 = np.array([-1, 0])
    # x0 = np.array([0, 0.5])
    # x0 = np.array([-1, -0.5])
    # x0 = np.array([0, 0])
    epsilon_g = 1e-6
    options = {
        'pen': 'int',
        'uh': 1,
        'ug': 3,
        'p': 0.5,
    }
    opt_options = {
        'step_init': 1,
        'linsearch': 'backtrack',
        'constraint': fn.e5_4_g
    }
    print(
        f"Interior penalty: {con_optimizer(e5_4, x0, epsilon_g, options, opt_options)}")

    # plot_constrained_opt(func, constraint_5_4, x0,
    #                      "Contour plot of the cross-sectional area with stress constraints")

    print("- Cantelever problem from 4.2")
    p4_2 = ConstrainedProblem(fn.p42_f, fn.p42_df, g=fn.p42_g, dg=fn.p42_dg)
    x0 = np.array([0.013, 0.004])
    epsilon_g = 1e-5
    options = {
        'pen': 'ext',
        'uh': 1,
        'ug': 0.5,
        'p': 1.1,
    }
    opt_options = {
        'step_init': 1,
        'constraint': fn.p42_g
    }

    print(
        f"Exterior penalty cantilever: {(con_optimizer(p4_2, x0, epsilon_g, options, opt_options))}")

    # print(check_grad(func, grad, [0, 0]))
    # print(check_grad(func, grad, [-0.5, 0.5]))
