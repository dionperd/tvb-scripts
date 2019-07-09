# coding=utf-8

from tvb_plot.head_plotter import HeadPlotter
from tvb_plot.timeseries_plotter import TimeseriesPlotter


class Plotter(object):

    def __init__(self, config=None):
        self.config = config

    def plot_head(self, head):
        return HeadPlotter(self.config).plot_head(head)

    def plot_ts(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_ts(*args, **kwargs)

    def plot_raster(self,  *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_raster( *args, **kwargs)

    def plot_trajectories(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_ts(*args, **kwargs)

    def plot_spectral_analysis_raster(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_spectral_analysis_raster(self, *args, **kwargs)

    def plot_timeseries(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_timeseries(*args, **kwargs)

    def plot_tvb_timeseries(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_tvb_timeseries(*args, **kwargs)

    def plot_timeseries_raster(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_timeseries_raster(*args, **kwargs)

    def plot_tvb_timeseries_raster(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_tvb_timeseries_raster(*args, **kwargs)

    def plot_timeseries_interactive(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_timeseries_interactive(*args, **kwargs)

    def plot_tvb_timeseries_interactive(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_tvb_timeseries_interactive(*args, **kwargs)

    def plot_power_spectra_interactive(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_power_spectra_interactive(*args, **kwargs)

    def plot_tvb_power_spectra_interactive(self, *args, **kwargs):
        return TimeseriesPlotter(self.config).plot_tvb_power_spectra_interactive(*args, **kwargs)
