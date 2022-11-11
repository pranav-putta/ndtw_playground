import math

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.widgets import Slider

from cdtw import compute_uniform_cdtw, interpolate_trajectory, compute_ndtw


class NDTWPlayground(object):
    u""" Matplotlib Draggable Points base from https://github.com/yuma-m/matplotlib-draggable-plot """

    def __init__(self):
        self._figure, self._axes, self.__line = None, None, [None, None]
        self._dragging_point = None
        self.__points = [{}, {}]
        self._selected_plot = 0
        self._colors = ['b', 'r']
        self.npts = 50
        self.sdist = 10

        self._init_plot()

    def _init_plot(self):
        self._figure = plt.figure("Draw plot")
        axes = self._figure.add_axes([0.075, 0.25, 0.85, 0.70])
        axes.set_xlim(0, 100)
        axes.set_ylim(0, 100)
        axes.grid(which="both")
        self._axes = axes

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self._figure.canvas.mpl_connect('key_press_event', self._on_keypress)

        self.npts_slider_ax = self._figure.add_axes([0.25, 0.15, 0.65, 0.03])
        self.npts_slider = Slider(self.npts_slider_ax, 'Num Points', 0, 500, valinit=self.npts, valstep=10)
        self.npts_slider.on_changed(self.npts_changed)

        self.sdist_slider_ax = self._figure.add_axes([0.25, 0.10, 0.65, 0.03])
        self.sdist_slider = Slider(self.sdist_slider_ax, 'Success dist', 0, 100, valinit=self.sdist, valstep=5)
        self.sdist_slider.on_changed(self.sdist_changed)
        plt.show()

    @property
    def _points(self):
        return self.__points[self._selected_plot]

    @property
    def _line(self):
        return self.__line[self._selected_plot]

    @_line.setter
    def _line(self, a):
        self.__line[self._selected_plot] = a

    def npts_changed(self, val):
        self.npts = val
        self._update_plot()

    def sdist_changed(self, val):
        self.sdist = val
        self._update_plot()

    def show_ndtw(self):
        if not (len(self.__points[0].items()) > 1 and len(self.__points[1].items()) > 1):
            return
        path1 = list(sorted(self.__points[0].items()))
        path2 = list(sorted(self.__points[1].items()))

        if self.npts > 0:
            ndtw, dtw = compute_uniform_cdtw(path1, path2, self.sdist, self.npts, return_dtw=True)
        else:
            ndtw, dtw = compute_ndtw(path1, path2, self.sdist, return_dtw=True)

        self._figure.suptitle(f'NDTW = {ndtw}; DTW = {dtw}')

    def _on_keypress(self, event):
        if event.key == 'enter':
            path1 = list(sorted(self.__points[0].items()))
            path2 = list(sorted(self.__points[1].items()))

            ndtw = compute_uniform_cdtw(path1, path2, self.sdist, self.npts)
            ap1 = list(interpolate_trajectory(path1, self.npts))
            ap2 = list(interpolate_trajectory(path2, self.npts))

            self.__line[0].set_data(*list(zip(*ap1)))
            self.__line[1].set_data(*list(zip(*ap2)))
            self.show_ndtw()
            self._figure.canvas.draw()
            print(ndtw)
        elif event.key == 'tab':
            self._selected_plot = (self._selected_plot + 1) % 2
        elif event.key == 'c':
            self._figure.clear()
            self.__init__()

    def _update_plot(self):
        tmp = self._selected_plot
        for i, points in enumerate(self.__points):
            self._selected_plot = i
            if not len(points):
                continue
            x, y = zip(*sorted(points.items()))
            # Add new plot
            if not self._line:
                self._line, = self._axes.plot(x, y, color=self._colors[i], marker="o", markersize=10)
            # Update current plot
            else:
                self._line.set_data(x, y)
        self._selected_plot = tmp
        self.show_ndtw()
        self._figure.canvas.draw()

    def _add_point(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)
        self._points[x] = y
        return x, y

    def _remove_point(self, x, _):
        if x in self._points:
            self._points.pop(x)

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 3.0
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for x, y in self._points.items():
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, event):
        u""" callback method for mouse click event
        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
            else:
                self._add_point(event)
            self._update_plot()
        # right click
        elif event.button == 3 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._remove_point(*point)
                self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self._dragging_point:
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._remove_point(*self._dragging_point)
        self._dragging_point = self._add_point(event)
        self._update_plot()


if __name__ == "__main__":
    plot = NDTWPlayground()
