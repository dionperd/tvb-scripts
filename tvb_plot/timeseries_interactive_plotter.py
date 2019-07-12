# coding=utf-8
import numpy

from tvb_utils.log_error_utils import initialize_logger
from tvb_utils.data_structures_utils import ensure_list, rotate_n_list_elements
from tvb.simulator.plot.timeseries_interactive import \
    TimeSeriesInteractive, pylab, time_series_datatypes, BACKGROUNDCOLOUR, EDGECOLOUR

from matplotlib.pyplot import rcParams


LOG = initialize_logger(__name__)


class TimeseriesInteractivePlotter(TimeSeriesInteractive):

    def create_figure(self, **kwargs):
        """ Create the figure and time-series axes. """
        # time_series_type = self.time_series.__class__.__name__
        figsize = kwargs.pop("figsize", (14, 8))
        facecolor = kwargs.pop("facecolor", BACKGROUNDCOLOUR)
        edgecolor = kwargs.pop("edgecolor", EDGECOLOUR)
        try:
            figure_window_title = "Interactive time series: "  # + time_series_type
            num = kwargs.pop("figname", kwargs.get("num", figure_window_title))
            #            pylab.close(figure_window_title)
            self.its_fig = pylab.figure(num=num,
                                        figsize=figsize,
                                        facecolor=facecolor,
                                        edgecolor=edgecolor)
        except ValueError:
            LOG.info("My life would be easier if you'd update your PyLab...")
            figure_number = 42
            pylab.close(figure_number)
            self.its_fig = pylab.figure(num=figure_number,
                                        figsize=figsize,
                                        facecolor=facecolor,
                                        edgecolor=edgecolor)

        self.ts_ax = self.its_fig.add_axes([0.1, 0.1, 0.85, 0.85])

        self.whereami_ax = self.its_fig.add_axes([0.1, 0.95, 0.85, 0.025],
                                                 facecolor=facecolor)
        self.whereami_ax.set_axis_off()
        if hasattr(self.whereami_ax, 'autoscale'):
            self.whereami_ax.autoscale(enable=True, axis='both', tight=True)
        self.whereami_ax.plot(self.time_view,
                              numpy.zeros((len(self.time_view),)),
                              color="0.3", linestyle="--")
        self.hereiam = self.whereami_ax.plot(self.time_view,
                                             numpy.zeros((len(self.time_view),)),
                                             'b-', linewidth=4)

    def plot_time_series(self, **kwargs):
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

        # Determine colors and linestyles for each variable of the Timeseries
        linestyle = ensure_list(kwargs.pop("linestyle", "-"))
        colors = kwargs.pop("linestyle", None)
        if colors is not None:
            colors = ensure_list(colors)
        if self.data.shape[1] > 1:
            linestyle = rotate_n_list_elements(linestyle, self.data.shape[1])
            if not isinstance(colors, list):
                colors = (rcParams['axes.prop_cycle']).by_key()['color']
            colors = rotate_n_list_elements(colors, self.data.shape[1])
        else:
            # If no color,
            # or a color sequence is given in the input
            # but there is only one variable to plot,
            # choose the black color
            if colors is None or len(colors) > 1:
                colors = ["k"]
            linestyle = linestyle[:1]

        # Determine the alpha value depending on the number of modes/samples of the Timeseries
        alpha = 1.0
        if len(self.data.shape) > 3 and self.data.shape[3] > 1:
            alpha /= self.data.shape[3]

        # Plot the timeseries per variable and sample
        self.ts_view = []
        for i_var in range(self.data.shape[1]):
            for ii in range(self.data.shape[3]):
                # Plot the timeseries
                self.ts_view.append(self.ts_ax.plot(self.time[self.time_view],
                                                    offset + self.data[self.time_view, i_var, :, ii],
                                                    alpha=alpha, color=colors[i_var], linestyle=linestyle[i_var],
                                                    **kwargs))

        self.hereiam[0].remove()
        self.hereiam = self.whereami_ax.plot(self.time_view,
                                             numpy.zeros((len(self.time_view),)),
                                             'b-', linewidth=4)

        pylab.draw()

    def show(self, block=True, **kwargs):
        """ Generate the interactive time-series figure. """
        time_series_type = self.time_series.__class__.__name__
        msg = "Generating an interactive time-series plot for %s"
        if isinstance(self.time_series, time_series_datatypes.TimeSeriesSurface):
            LOG.warning("Intended for region and sensors, not surfaces.")
        LOG.info(msg % time_series_type)

        # Make the figure:
        self.create_figure()

        # Selectors
        # self.add_mode_selector()

        # Sliders
        self.add_window_length_slider()
        self.add_scaling_slider()
        # self.add_time_slider()

        # time-view buttons
        self.add_step_back_button()
        self.add_step_forward_button()
        self.add_big_step_back_button()
        self.add_big_step_forward_button()
        self.add_start_button()
        self.add_end_button()

        # Plot timeseries
        self.plot_time_series()

        pylab.show(block=block, **kwargs)
