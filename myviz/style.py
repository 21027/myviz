import matplotlib.pyplot as plt

def apply_style():
    plt.style.use("default")

    plt.rcParams.update({
        "figure.figsize": (8, 5),
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "lines.linewidth": 2,
        "font.family": "sans-serif"
    })
