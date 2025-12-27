import matplotlib.pyplot as plt
from .style import apply_style

def styled_hist(data, bins=10, title=""):
    apply_style()
    plt.hist(data, bins=bins)
    plt.title(title)
    plt.show()
