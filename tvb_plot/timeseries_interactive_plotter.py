# coding=utf-8
import numpy

from tvb.simulator.plot.timeseries_interactive import TimeSeriesInteractive, pylab


class TimeseriesInteractivePlotter(TimeSeriesInteractive):

    def plot_time_series(self):
        """ Plot a view on the timeseries. """
        # Set title and axis labels
        #time_series_type = self.time_series.__class__.__name__
        #self.ts_ax.set(title = time_series_type)
        #self.ts_ax.set(xlabel = "Time (%s)" % self.units)

        # This assumes shape => (time, space)
        step = self.scaling * self.peak_to_peak
        if step == 0:
            offset = 0.0
        else: #NOTE: specifying step in arange is faster, but it fence-posts.
            offset = numpy.arange(0, self.nsrs) * step
        if hasattr(self.ts_ax, 'autoscale'):
            self.ts_ax.autoscale(enable=True, axis='both', tight=True)

        self.ts_ax.set_yticks(offset)
        self.ts_ax.set_yticklabels(self.labels, fontsize=10)
        #import pdb; pdb.set_trace()

        #Light gray guidelines
        self.ts_ax.plot([self.nsrs*[self.time[self.time_view[0]]],
                         self.nsrs*[self.time[self.time_view[-1]]]],
                         numpy.vstack(2*(offset,)), "0.85")

        data_shape = self.data.shape
        if len(data_shape) > 3 and data_shape[3] > 1:
            alpha = 1/data_shape[3]
            self.ts_view = []
            for ii in range(data_shape[3]):
                # Plot the timeseries
                self.ts_view.append(self.ts_ax.plot(self.time[self.time_view],
                                                    offset + self.data[self.time_view, 0, :, ii],
                                                    alpha=alpha))
        #Plot the timeseries
        self.ts_view = self.ts_ax.plot(self.time[self.time_view],
                                       offset + self.data[self.time_view, 0, :, 0])

        self.hereiam[0].remove()
        self.hereiam = self.whereami_ax.plot(self.time_view,
                                             numpy.zeros((len(self.time_view),)),
                                             'b-', linewidth=4)

        pylab.draw()
