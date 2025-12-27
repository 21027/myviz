import matplotlib.pyplot as plt
from .style import apply_style

def styled_bar(categories, values, title=""):
    apply_style()
    plt.bar(categories, values)
    plt.title(title)
    plt.show()
