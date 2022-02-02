import matplotlib.pyplot as plt
import numpy as np

from flask import current_app

# has-dependency to-be deprecated file. Useful for generating graphs. Now they are implemented
#  through d3.js for flexibility.


def category_frequency_plot(values):

    plot_values = values
    data = [x for x in plot_values]

    count = [int(x[0]) for x in data]
    categories = [x[1] for x in data]

    fig1, ax1 = plt.subplots()
    ax1.pie(count, labels=categories, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    ax1.set_title("Expenses by Categories")

    plt.savefig(current_app.root_path + '/static/graphs/category_frequency.png', bbox_inches='tight')
    plt.close(fig1)


def item_frequency_plot(values):

    plot_values = values
    data = [x for x in plot_values]

    count = [int(x[0]) for x in data]
    categories = [x[1] for x in data]

    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    wedges, texts, autotexts = ax.pie(count, wedgeprops=dict(width=0.5), startangle=-40, autopct='%1.f%%', pctdistance=0.8)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(categories[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Expenses by Items")

    plt.savefig(current_app.root_path + '/static/graphs/item_frequency.png', bbox_inches='tight')
    plt.close(fig)
