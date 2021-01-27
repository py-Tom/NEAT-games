"""Calculates the coefficients a, b, c of the quadratic equation y = ax^2 + bx + c."""

import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


AIRTIME = 70
MAX_HEIGHT = 50


def parabola_coeff(eq):

    a = eq[0]
    b = eq[1]
    c = eq[2]

    F = np.empty(3)
    try:
        F[0] = -b / (2 * a) - (AIRTIME / 2)
        F[1] = -(((b ** 2) - (4 * a * c)) / (4 * a)) - MAX_HEIGHT
        F[2] = -b - (((b * b) - (4 * a * c)) ** 0.5) / (2 * a)
        # F[2] = -b + (((b * b) - (4 * a * c)) ** 0.5) / (2 * a)
    except ValueError:
        print("pass")
        pass

    return F


if __name__ == "__main__":
    eq_guess = np.array([-0.46, 21.5, 0.1])

    eq = fsolve(parabola_coeff, eq_guess)
    a = eq[0]
    b = eq[1]
    c = eq[2]
    print(eq)
    print(np.isclose(parabola_coeff(eq), [0.0, 0.0, 0.0]))

    x = np.linspace(-2, AIRTIME + 2, 100)
    y = a * x ** 2 + b * x + c

    delta = b ** 2 - 4 * a * c
    sqrt_delta = delta ** 0.5
    x_01 = (round((-b - sqrt_delta) / (2 * a), 2), 0.00)
    x_02 = (round((-b + sqrt_delta) / (2 * a), 2), 0.00)
    peak = (round(-b / (2 * a), 2), round(-delta / (4 * a), 2))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.spines["left"].set_position(("data", 0))
    ax.spines["right"].set_color("none")
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["top"].set_color("none")
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")

    plt.plot(x, y, "r")
    plt.plot(x_01[0], x_01[1], "ob")
    plt.text(x_01[0], x_01[1] + 2, x_01, fontsize=12)
    plt.plot(x_02[0], x_02[1], "ob")
    plt.text(x_02[0], x_02[1] + 2, x_02, fontsize=12)
    plt.plot(peak[0], peak[1], "ob")
    plt.text(peak[0], peak[1] + 2, peak, fontsize=12)

    plt.show()
