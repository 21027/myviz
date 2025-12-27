import matplotlib.pyplot as plt
from .style import apply_style

def styled_scatter(x, y, title=""):
    apply_style()
    plt.scatter(x, y)
    plt.title(title)
    plt.show()
