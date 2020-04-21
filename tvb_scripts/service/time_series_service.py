# -*- coding: utf-8 -*-
from copy import deepcopy
from six import string_types
from collections import OrderedDict

import numpy as np
from scipy.signal import convolve, detrend, hilbert

from tvb_scripts.utils.log_error_utils import raise_value_error, initialize_logger
from tvb_scripts.utils.data_structures_utils import ensure_list
# from tvb_scripts.utils.computations_utils import select_greater_values_array_inds, \
#     select_by_hierarchical_group_metric_clustering
from tvb_scripts.utils.time_series_utils import abs_envelope, spectrogram_envelope, filter_data, \
    decimate_signals, normalize_signals
from tvb_scripts.datatypes.time_series import TimeSeriesSEEG, LABELS_ORDERING


class TimeSeriesService(object):
    logger = initialize_logger(__name__)

    def __init__(self, logger=initialize_logger(__name__)):
        self.logger = logger

    def decimate(self, time_series, decim_ratio, **kwargs):
        if decim_ratio > 1:
            return time_series.duplicate(data=time_series.data[0:time_series.time_length:decim_ratio],
                                         sample_period=float(decim_ratio*time_series.sample_period), **kwargs)
        else:
            return time_series.duplicate()

    def decimate_by_filtering(self, time_series, decim_ratio, **kwargs):
        if decim_ratio > 1:
            decim_data, decim_time, decim_dt, decim_n_times = decimate_signals(time_series.squeezed,
                                                                               time_series.time, decim_ratio)
            return time_series.duplicate(data=decim_data, sample_period=float(decim_dt), **kwargs)
        else:
            return time_series.duplicate(**kwargs)

    def convolve(self, time_series, win_len=None, kernel=None, **kwargs):
        n_kernel_points = np.int(np.round(win_len))
        if kernel is None:
            kernel = np.ones((n_kernel_points, 1, 1, 1)) / n_kernel_points
        else:
            kernel = kernel * np.ones((n_kernel_points, 1, 1, 1))
        return time_series.duplicate(data=convolve(time_series.data, kernel, mode='same'), **kwargs)

    def hilbert_envelope(self, time_series, **kwargs):
        return time_series.duplicate(data=np.abs(hilbert(time_series.data, axis=0)), **kwargs)

    def spectrogram_envelope(self, time_series, lpf=None, hpf=None, nperseg=None, **kwargs):
        data, time = spectrogram_envelope(time_series.squeezed, time_series.sample_rate, lpf, hpf, nperseg)
        if len(time_series.sample_period_unit) > 0 and time_series.sample_period_unit[0] == "m":
            time *= 1000
        return time_series.duplicate(data=data, start_time=time_series.start_time + time[0],
                                     sample_period=np.diff(time).mean(), **kwargs)

    def abs_envelope(self, time_series, **kwargs):
        return time_series.duplicate(data=abs_envelope(time_series.data), **kwargs)

    def detrend(self, time_series, type='linear', **kwargs):
        return time_series.duplicate(data=detrend(time_series.data, axis=0, type=type), **kwargs)

    def normalize(self, time_series, normalization=None, axis=None, percent=None, **kwargs):
        return time_series.duplicate(data=normalize_signals(time_series.data, normalization, axis, percent), **kwargs)

    def filter(self, time_series, lowcut=None, highcut=None, mode='bandpass', order=3, **kwargs):
        return time_series.duplicate(data=filter_data(time_series.data, time_series.sample_rate,
                                                     lowcut, highcut, mode, order), **kwargs)

    def log(self, time_series, **kwargs):
        return time_series.duplicate(data=np.log(time_series.data), **kwargs)

    def exp(self, time_series, **kwargs):
        return time_series.duplicate(data=np.exp(time_series.data), **kwargs)

    def abs(self, time_series, **kwargs):
        return time_series.duplicate(data=np.abs(time_series.data), **kwargs)

    def power(self, time_series):
        return np.sum(self.square(self.normalize(time_series, "mean", axis=0)).squeezed, axis=0)

    def square(self, time_series, **kwargs):
        return time_series.duplicate(data=time_series.data ** 2, **kwargs)

    def correlation(self, time_series):
        return np.corrcoef(time_series.squeezed.T)

    def compute_across_dimension(self, time_series, dimension_name_or_index, fun, fun_name, **kwargs):
        labels_ordering = deepcopy(time_series.labels_ordering)
        labels_dimensions = deepcopy(time_series.labels_dimensions)
        if isinstance(dimension_name_or_index, string_types):
            # dimension_name_or_index == dimension_name
            dimension_name = dimension_name_or_index
            dimension_index = labels_ordering.index(dimension_name)
        else:
            # dimension_name_or_index == dimension_index
            dimension_index = dimension_name_or_index
            dimension_name = time_series.get_dimension_name(dimension_name_or_index)
        try:
            del labels_dimensions[dimension_name]
        except:
            pass
        labels_dimensions[dimension_name] = [fun_name]
        data = np.expand_dims(fun(time_series.data, axis=dimension_index), dimension_index)
        return time_series.duplicate(data=data,
                                     labels_ordering=kwargs.pop("labels_ordering", labels_ordering),
                                     labels_dimensions=kwargs.pop("labels_dimensions", labels_dimensions), **kwargs)

    def mean_across_dimension(self, time_series, dimension_name_or_index, **kwargs):
        return self.compute_across_dimension(time_series, dimension_name_or_index, np.mean, "Mean", **kwargs)

    def min_across_dimension(self, time_series, dimension_name_or_index, **kwargs):
        return self.compute_across_dimension(time_series, dimension_name_or_index, np.min, "Minimum", **kwargs)

    def max_across_dimension(self, time_series, dimension_name_or_index, **kwargs):
        return self.compute_across_dimension(time_series, dimension_name_or_index, np.max, "Maximum", **kwargs)

    def sum_across_dimension(self, time_series, dimension_name_or_index, **kwargs):
        return self.compute_across_dimension(time_series, dimension_name_or_index, np.sum, "Sum", **kwargs)

    def _compile_select_funs(self, labels_ordering, **kwargs):
        select_funs = []
        for dim, lbl in enumerate(labels_ordering):
            indices_labels_slices = ensure_list(kwargs.pop(lbl, []))
            if len(indices_labels_slices) > 0:
                select_funs.append(lambda ts: getattr(ts, "slice_data_across_dimension")(indices_labels_slices, dim))
        return select_funs

    def select(self, time_series, select_funs=None, **kwargs):
        if select_funs is None:
            select_funs = self._compile_select_funs(time_series.labels_ordering, **kwargs)
        for fun in select_funs:
            time_series = fun(time_series)
        return time_series, select_funs

    def concatenate(self, time_series_list, dim, **kwargs):
        time_series_list = ensure_list(time_series_list)
        n_ts = len(time_series_list)
        if n_ts > 0:
            out_time_series, select_funs = self.select(time_series_list[0], **kwargs)
            if n_ts > 1:
                for id, time_series in enumerate(time_series_list[1:]):
                    if np.float32(out_time_series.sample_period) != np.float32(time_series.sample_period):
                        raise_value_error("Timeseries concatenation failed!\n"
                                          "Timeseries %d have a different time step %s \n "
                                          "than the concatenated ones %s!" %
                                          (id, str(np.float32(time_series.sample_period)),
                                           str(np.float32(out_time_series.sample_period))))
                    else:
                        time_series = self.select(time_series, select_funs)[0]
                        # try:
                        out_time_series.data = np.concatenate([out_time_series.data, time_series.data], axis=dim)
                        if len(out_time_series.get_dimension_labels(dim)) > 0:
                            if len(time_series.get_dimension_labels(dim)) > 0:
                                dim_label = out_time_series.get_dimension_name(dim)
                                out_time_series.labels_dimensions[dim_label] = \
                                    np.array(ensure_list(out_time_series.get_dimension_labels(dim)) +
                                             ensure_list(time_series.get_dimension_labels(dim)))
                            else:
                                raise_value_error("TimeSeries to concatenate %s \n "
                                                  "has no dimension labels across the concatenation axis,\n"
                                                  "unlike the TimeSeries to be appended to: %s!"
                                                  % (str(time_series), str(out_time_series)))
                        # except:
                        #     raise_value_error("Timeseries concatenation failed!\n"
                        #                       "Timeseries %d have a shape %s and the concatenated ones %s!" %
                        #                       (id, str(out_time_series.shape), str(time_series.shape)))
                return out_time_series
            else:
                return out_time_series
        else:
            raise_value_error("Cannot concatenate empty list of TimeSeries!")

    def concatenate_in_time(self, time_series_list, **kwargs):
        return self.concatenate(time_series_list, 0, **kwargs)

    def concatenate_variables(self, time_series_list, **kwargs):
        return self.concatenate(time_series_list, 1, **kwargs)

    def concatenate_in_space(self, time_series_list, **kwargs):
        return self.concatenate(time_series_list, 2, **kwargs)

    def concatenate_samples(self, time_series_list, **kwargs):
        return self.concatenate(time_series_list, 3, **kwargs)

    def concatenate_modes(self, time_series_list, **kwargs):
        return self.concatenate(time_series_list, 3, **kwargs)

    # def select_by_metric(self, time_series, metric, metric_th=None, metric_percentile=None, nvals=None):
    #     selection = np.unique(select_greater_values_array_inds(metric, metric_th, metric_percentile, nvals))
    #     return time_series.get_subspace_by_index(selection), selection
    #
    # def select_by_power(self, time_series, power=np.array([]), power_th=None):
    #     if len(power) != time_series.number_of_labels:
    #         power = self.power(time_series)
    #     return self.select_by_metric(time_series, power, power_th)
    #
    # def select_by_hierarchical_group_metric_clustering(self, time_series, distance, disconnectivity=np.array([]),
    #                                                    metric=None, n_groups=10, members_per_group=1):
    #     selection = np.unique(select_by_hierarchical_group_metric_clustering(distance, disconnectivity, metric,
    #                                                                          n_groups, members_per_group))
    #     return time_series.get_subspace_by_index(selection), selection
    #
    # def select_by_correlation_power(self, time_series, correlation=np.array([]), disconnectivity=np.array([]),
    #                                 power=np.array([]), n_groups=10, members_per_group=1):
    #     if correlation.shape[0] != time_series.number_of_labels:
    #         correlation = self.correlation(time_series)
    #     if len(power) != time_series.number_of_labels:
    #         power = self.power(time_series)
    #     return self.select_by_hierarchical_group_metric_clustering(time_series, 1 - correlation,
    #                                                                disconnectivity, power, n_groups, members_per_group)
    #
    # def select_by_projection_power(self, time_series, projection=np.array([]),
    #                                disconnectivity=np.array([]), power=np.array([]),
    #                                n_groups=10, members_per_group=1):
    #     if len(power) != time_series.number_of_labels:
    #         power = self.power(time_series)
    #     return self.select_by_hierarchical_group_metric_clustering(time_series, 1 - np.corrcoef(projection),
    #                                                                disconnectivity, power, n_groups, members_per_group)
    #
    # def select_by_rois_proximity(self, time_series, proximity, proximity_th=None, percentile=None, n_signals=None):
    #     initial_selection = range(time_series.number_of_labels)
    #     selection = []
    #     for prox in proximity:
    #         selection += (
    #             np.array(initial_selection)[select_greater_values_array_inds(prox, proximity_th,
    #                                                                          percentile, n_signals)]).tolist()
    #     selection = np.unique(selection)
    #     return time_series.get_subspace_by_index(selection), selection
    #
    # def select_by_rois(self, time_series, rois, all_labels):
    #     for ir, roi in rois:
    #         if not (isinstance(roi, string_types)):
    #             rois[ir] = all_labels[roi]
    #     return time_series.get_subspace_by_label(rois), rois

    def compute_seeg(self, source_time_series, sensors, projection=None, sum_mode="lin", **kwargs):
        if np.all(sum_mode == "exp"):
            seeg_fun = lambda source, projection_data: self.compute_seeg_exp(source.squeezed, projection_data)
        else:
            seeg_fun = lambda source, projection_data: self.compute_seeg_lin(source.squeezed, projection_data)
        labels_ordering = LABELS_ORDERING
        labels_ordering[1] = "SEEG"
        labels_ordering[2] = "SEEG Sensor"
        kwargs.update({"labels_ordering": labels_ordering,
                       "start_time": source_time_series.start_time,
                       "sample_period": source_time_series.sample_period,
                       "sample_period_unit": source_time_series.sample_period_unit})
        if isinstance(sensors, dict):
            seeg = OrderedDict()
            for sensor, projection in sensors.items():
                kwargs.update({"labels_dimensions": {labels_ordering[2]: sensor.labels,
                                                     labels_ordering[1]: [sensor.name]},
                               "sensors": sensor})
                seeg[sensor.name] = \
                    source_time_series.__class__(
                        np.expand_dims(seeg_fun(source_time_series, projection.projection_data), 1), **kwargs)
            return seeg
        else:
            kwargs.update({"labels_dimensions": {labels_ordering[2]: sensors.labels,
                                                 labels_ordering[1]: [sensors.name]},
                           "sensors": sensors})
            return TimeSeriesSEEG(
                np.expand_dims(seeg_fun(source_time_series, projection.projection_data), 1), **kwargs)

    def compute_seeg_lin(self, source_time_series, projection_data):
        return source_time_series.dot(projection_data.T)

    def compute_seeg_exp(self, source_time_series, projection_data):
        return np.log(np.exp(source_time_series).dot(projection_data.T))
