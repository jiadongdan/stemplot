import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

class UnetDiagram:

    def __init__(self, encoder_color='C0', decoder_color='C1', ec=None, lw=1):
        self.encoder_color = encoder_color
        self.decoder_color = decoder_color
        self.ec = ec
        self.lw = lw

    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.2))

        d = 0.25
        dx = 0.5

        s1 = 1.5
        xy1 = np.array([(-dx * s1, -d * 3 * s1), (-dx * s1, +d * 3 * s1), (dx * s1, d * s1), (dx * s1, -d * s1)])
        xy2 = xy1.copy()
        xy2[:, 0] = -xy2[:, 0]
        xy1[:, 0] -= 0.5
        xy2[:, 0] += 0.5

        ax.add_patch(Polygon(xy=xy1, facecolor=self.encoder_color, edgecolor='#2d3742', zorder=-1))
        ax.add_patch(Polygon(xy=xy2, facecolor=self.decoder_color, edgecolor='#2d3742', zorder=-1))

