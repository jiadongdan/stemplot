class Transform:

    def __init__(self, ax):
        self.ax = ax
        self.fig = ax.figure

        self._transdict = dict(ax2data=self.ax.transLimits.inverted(),
                               data2ax=self.ax.transLimits,
                               ax2pixel=self.ax.transAxes,
                               pixel2ax=self.ax.transAxes.inverted(),
                               data2pixel=self.ax.transData,
                               pixel2data=self.ax.transData.inverted(),
                               fig2pixel=self.fig.transFigure,
                               pixel2fig=self.fig.transFigure.inverted(),
                               inch2pixel=self.fig.dpi_scale_trans,
                               pixel2inch=self.fig.dpi_scale_trans.inverted(),
                               fig2data=self.fig.transFigure+self.ax.transData.inverted(),
                               data2fig=self.ax.transData+self.fig.transFigure.inverted(),
                               fig2inch=self.fig.transFigure+self.fig.dpi_scale_trans.inverted(),
                               ax2fig=self.ax.transAxes+self.fig.transFigure.inverted(),
                              )

    def transform(self, xy, kind='fig2pixel'):
        trans = self._transdict[kind]
        return trans.transform(xy)