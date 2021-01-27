"""Calculates the coefficients a, b, c of the quadratic equation y = ax^2 + bx + c."""

import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


airtime = 30
max_height = 100


def parabola_coeff(eq):

    a = eq[0]
    b = eq[1]
    c = eq[2]

    F = np.empty(3)
    try:
        F[0] = -b / 2 / a - (airtime / 2)
        F[1] = -(((b ** 2) - (4 * a * c)) / (4 * a)) - max_height
        F[2] = -b - (((b * b) - (4 * a * c)) ** 0.5) / (2 * a)
    except ValueError:
        print("pass")
        pass

    return F


if __name__ == "__main__":
    eq_guess = np.array([-0.4, 15, -30])
    eq = fsolve(parabola_coeff, eq_guess)
    print(eq)
    print(eq[0])
    print(eq[1])
    print(eq[2])
    print(np.isclose(parabola_coeff(eq), [0.0, 0.0, 0.0]))

    x = np.linspace(-2, airtime + 2, 100)
    # y = x ** 2
    y = eq[0] * x ** 2 + eq[1] * x + eq[2]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.spines["left"].set_position(("data", 0))
    ax.spines["right"].set_color("none")
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["top"].set_color("none")
    ax.spines["left"].set_smart_bounds(True)
    ax.spines["bottom"].set_smart_bounds(True)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    plt.plot(x, y, "r")
    plt.plot(airtime, 0, "ob")
    plt.text(airtime, -10, "(30, 0)", fontsize=12)
    plt.plot(0, 0, "ob")
    plt.text(0, -10, "(0, 0)", fontsize=12)
    plt.plot(airtime / 2, max_height, "ob")
    plt.text(airtime / 2, -10, "(15, 100)", fontsize=12)
    plt.show()
