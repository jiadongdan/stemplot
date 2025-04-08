import matplotlib.pyplot as plt
import os

def set_style(name="rc1"):
    """Apply a .mplstyle file from the style folder."""
    style_dir = os.path.dirname(__file__)
    style_path = os.path.join(style_dir, f"{name}.mplstyle")
    if os.path.exists(style_path):
        plt.style.use(style_path)
    else:
        raise FileNotFoundError(f"Style '{name}' not found in {style_dir}")
