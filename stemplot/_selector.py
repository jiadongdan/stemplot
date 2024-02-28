from matplotlib.widgets import RectangleSelector


class FigRectSelector(RectangleSelector):

    def __init__(self, fig):
        ax = fig.add_axes([0, 0, 1, 1], fc=[0, 0, 0, 0])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        RectangleSelector.__init__(self, ax, self.onselect, interactive=True)

    def onselect(self, eclick, erelease):
        # print(eclick.xdata, eclick.ydata)
        # print(erelease.xdata, erelease.ydata)

        x = min(eclick.xdata, erelease.xdata)
        y = min(eclick.ydata, erelease.ydata)
        w = abs(eclick.xdata - erelease.xdata)
        h = abs(eclick.ydata - erelease.ydata)
        print('ax = fig.add_axes([{:3.3f}, {:3.3f}, {:3.3f}, {:3.3f}])'.format(x, y, w, h))
