import matplotlib.pyplot as plt
import numpy as np

# statistical constants for XMR charts
d2 = 1.128
D3 = 0
D4 = 3.267

class XMR:
    """ class to create a simple XMR control chart from an array of data """
    def __init__(self, data, index=None):

        self.data = data
        if index is None:
            index = list(range(len(self.data)))
        self.index = index
        self.data_mr = self.moving_range(data)
    
    @staticmethod
    def moving_range(data):
        return abs(data[1:] - data[:-1])

    @staticmethod
    def plot_chart(data, index, center, ucl, lcl, axes=None, **kwargs):
        if axes is None:
            fig,axes = plt.subplots(1,1)

        axes.plot(index, data, marker='o', **kwargs)
        axes.axhline(center, **kwargs)
        axes.axhline(ucl, **kwargs)
        axes.axhline(lcl, **kwargs)
        return axes

    def xlimits(self):
        mrbar,_,_ = self.mrlimits(self.data_mr)
        xbar = np.mean(self.data)
        ucl = xbar + 3*mrbar/d2
        lcl = xbar - 3*mrbar/d2
        return xbar, ucl, lcl

    def xchart(self, axes=None, **kwargs):
        xbar, ucl, lcl = self.xlimits()
        data = self.data
        index = self.index

        axes = self.plot_chart(self.data, self.index, xbar, ucl, lcl, axes, **kwargs)  

        ooc = (data<lcl) | (data>ucl)
        if any(ooc):
            axes.scatter(x=index[ooc], y=data[ooc], marker='o', color='red', zorder=10)
        return axes


    def mrlimits(self, data):
        mrbar = np.mean(data)
        ucl = D4*mrbar
        lcl = D3*mrbar

        ooc = (data<lcl) | (data>ucl)
        while any(ooc):
            data = data[~ooc]
            mrbar, ucl, lcl = self.mrlimits(data)
            ooc = (data<lcl) | (data>ucl)

        return mrbar, ucl, lcl

    def mrchart(self, axes=None, **kwargs):
        data = self.data_mr
        index = self.index[1:]
        mrbar, ucl, lcl = self.mrlimits(data)

        axes = self.plot_chart(data, index, mrbar, ucl, lcl, axes, **kwargs)

        ooc = (data<lcl) | (data>ucl)
        if any(ooc):
            axes.scatter(x=index[ooc], y=data[ooc], marker='o', color='red', zorder=10)

        return axes
