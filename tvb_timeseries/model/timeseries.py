# coding=utf-8
from six import string_types
from enum import Enum
from copy import deepcopy

import numpy

from tvb.basic.profile import TvbProfile

TvbProfile.set_profile(TvbProfile.LIBRARY_PROFILE)

from tvb_utils.log_error_utils import initialize_logger, raise_value_error, warning
from tvb_utils.data_structures_utils import isequal_string, monopolar_to_bipolar

from tvb.datatypes.time_series import \
    TimeSeries, TimeSeriesRegion, TimeSeriesEEG, TimeSeriesMEG, TimeSeriesSEEG, TimeSeriesSurface, TimeSeriesVolume


class TimeseriesDimensions(Enum):
    TIME = "Time"
    SPACE = "Space"
    VARIABLES = "State Variables"
    SAMPLES = "Samples"


LABELS_ORDERING = [TimeseriesDimensions.TIME.value,
                   TimeseriesDimensions.SPACE.value,
                   TimeseriesDimensions.VARIABLES.value,
                   TimeseriesDimensions.SAMPLES.value]


class PossibleVariables(Enum):
    LFP = "lfp"
    SOURCE = "source"
    EEG = "eeg"
    MEEG = "meeg"
    SEEG = "seeg"


def prepare_4D(data, logger=initialize_logger(__name__)):
    if data.ndim < 2:
        logger.error("The data array is expected to be at least 2D!")
        raise ValueError
    if data.ndim < 4:
        if data.ndim == 2:
            data = numpy.expand_dims(data, 2)
        data = numpy.expand_dims(data, 3)
    return data


class Timeseries(object):

    logger = initialize_logger(__name__)

    ts_type = ""

    # labels_dimensions = {"space": numpy.array([]), "variables": numpy.array([])}

    def __init__(self, data, **kwargs):
        data = prepare_4D(data, self.logger)
        time = kwargs.pop("time", None)
        if time is not None:
            time_start = kwargs.pop("start_time",  kwargs.pop("start_time", time[0]))
            time_step = kwargs.pop("sample_period", kwargs.pop("sample_period", numpy.mean(numpy.diff(time))))
            kwargs.update({"start_time": time_start, "sample_period": time_step})

        self.ts_type = kwargs.pop("ts_type", "Region")
        sensors = kwargs.get("sensors", None)
        labels_ordering = kwargs.pop("labels_ordering", None)
        if sensors is not None:
            if labels_ordering is None:
                labels_ordering = LABELS_ORDERING
                labels_ordering[1] = "%s sensor" % sensors.sensors_type
                kwargs.update({"labels_ordering": labels_ordering})
            if isequal_string(sensors.sensors_type, "SEEG") or \
                isequal_string(sensors.sensors_type, "Internal"):
                self._tvb = TimeSeriesSEEG(data, **kwargs)
                self.ts_type = "SEEG"
            elif isequal_string(sensors.sensors_type, "EEG"):
                self._tvb = TimeSeriesEEG(data, **kwargs)
                self.ts_type = "EEG"
            elif isequal_string(sensors.sensors_type, "MEG"):
                self._tvb = TimeSeriesMEG(data, **kwargs)
                self.ts_type = "MEG"
            else:
                raise_value_error("Not recognizing sensors of type %s:\n%s"
                                  % (sensors.sensors_type, str(sensors)))
        else:
            if isequal_string(self.ts_type, "Region"):
                if labels_ordering is None:
                    labels_ordering = LABELS_ORDERING
                    labels_ordering[1] = "Region"
                    kwargs.update({"labels_ordering": labels_ordering})
                self._tvb = TimeSeriesRegion(data=data, **kwargs)  # , **kwargs
            elif isequal_string(self.ts_type, "Surface"):
                if labels_ordering is None:
                    labels_ordering = LABELS_ORDERING
                    labels_ordering[1] = "Vertex"
                    kwargs.update({"labels_ordering": labels_ordering})
                self._tvb = TimeSeriesSurface(data, **kwargs)
            elif isequal_string(self.ts_type, "Volume"):
                if labels_ordering is None:
                    labels_ordering = ["Time", "X", "Y", "Z"]
                    kwargs.update({"labels_ordering": labels_ordering})
                self._tvb = TimeSeriesVolume(data, **kwargs)
            else:
                self._tvb = TimeSeries(data, **kwargs)

        if not numpy.all([dim_label in self._tvb.labels_ordering for dim_label in self._tvb.labels_dimensions.keys()]):
            warning("Lack of correspondance between timeseries labels_ordering %s\n"
                    "and labels_dimensions!: %s" % (self._tvb.labels_ordering, self._tvb.labels_dimensions.keys()))

        self.configure_time()
        self.configure_sampling_frequency()
        self._tvb.configure()
        self.configure_sample_rate()

    def _get_index_of_state_variable(self, sv_label):
        try:
            sv_index = \
                numpy.where(self._tvb.labels_dimensions[TimeseriesDimensions.VARIABLES.value] == sv_label)[0][0]
        except KeyError:
            self.logger.error("There are no state variables defined for this instance. Its shape is: %s",
                              self._tvb.data.shape)
            raise
        except IndexError:
            self.logger.error("Cannot access index of state variable label: %s. Existing state variables: %s" % (
                sv_label, self._tvb.labels_dimensions[TimeseriesDimensions.VARIABLES.value]))
            raise
        return sv_index

    def get_state_variable(self, sv_label):
        sv_data = self._tvb.data[:, :, self._get_index_of_state_variable(sv_label), :]
        subspace_labels_dimensions = deepcopy(self._tvb.labels_dimensions)
        subspace_labels_dimensions[TimeseriesDimensions.VARIABLES.value] = numpy.array([sv_label])
        if sv_data.ndim == 3:
            sv_data = numpy.expand_dims(sv_data, 2)
        return self.__class__(sv_data, labels_dimensions=subspace_labels_dimensions,
                              time=self._tvb.time, ts_type=self.ts_type)

    def _get_indices_for_labels(self, list_of_labels):
        list_of_indices_for_labels = []
        for label in list_of_labels:
            try:
                space_index = \
                    numpy.where(self._tvb.labels_dimensions[TimeseriesDimensions.SPACE.value] ==
                                label)[0][0]
            except ValueError:
                self.logger.error("Cannot access index of space label: %s. Existing space labels: %s" % (
                    label, self._tvb.labels_dimensions[TimeseriesDimensions.SPACE.value]))
                raise
            list_of_indices_for_labels.append(space_index)
        return list_of_indices_for_labels

    def get_subspace_by_labels(self, list_of_labels):
        list_of_indices_for_labels = self._get_indices_for_labels(list_of_labels)
        subspace_data = self._tvb.data[:, list_of_indices_for_labels, :, :]
        subspace_labels_dimensions = deepcopy(self._tvb.labels_dimensions)
        subspace_labels_dimensions[TimeseriesDimensions.SPACE.value] = numpy.array(list_of_labels)
        if subspace_data.ndim == 3:
            subspace_data = numpy.expand_dims(subspace_data, 1)
        return self.__class__(subspace_data, labels_dimensions=subspace_labels_dimensions,
                              time=self._tvb.time, ts_type=self.ts_type)

    def __getattr__(self, attr_name):
        state_variables_keys = []
        if TimeseriesDimensions.VARIABLES.value in self._tvb.labels_dimensions.keys():
            state_variables_keys = self._tvb.labels_dimensions[TimeseriesDimensions.VARIABLES.value]
            if attr_name in self._tvb.labels_dimensions[TimeseriesDimensions.VARIABLES.value]:
                return self.get_state_variable(attr_name)
        space_keys = []
        if (TimeseriesDimensions.SPACE.value in self._tvb.labels_dimensions.keys()):
            space_keys = self._tvb.labels_dimensions[TimeseriesDimensions.SPACE.value]
            if attr_name in self._tvb.labels_dimensions[TimeseriesDimensions.SPACE.value]:
                return self.get_subspace_by_labels([attr_name])
        try:
            return getattr(self._tvb, attr_name)
        except:
            # Hack to avoid stupid error messages when searching for __ attributes in numpy.array() call...
            # TODO: something better? Maybe not needed if we never do something like numpy.array(timeseries)
            if attr_name.find("__") < 0:
                self.logger.error(
                    "Attribute %s is not defined for this instance! You can use the following labels: "
                    "state_variables = %s and space = %s" %
                    (attr_name, state_variables_keys, space_keys))
            raise AttributeError

    def _get_index_for_slice_label(self, slice_label, slice_idx):
        if slice_idx == 1:
            return self._get_indices_for_labels([slice_label])[0]
        if slice_idx == 2:
            return self._get_index_of_state_variable(slice_label)

    def _check_for_string_slice_indices(self, current_slice, slice_idx):
        slice_label1 = current_slice.start
        slice_label2 = current_slice.stop

        if isinstance(slice_label1, string_types):
            slice_label1 = self._get_index_for_slice_label(slice_label1, slice_idx)
        if isinstance(slice_label2, string_types):
            slice_label2 = self._get_index_for_slice_label(slice_label2, slice_idx)

        return slice(slice_label1, slice_label2, current_slice.step)

    def _get_string_slice_index(self, current_slice_string, slice_idx):
        return self._get_index_for_slice_label(current_slice_string, slice_idx)

    def __getitem__(self, slice_tuple):
        slice_list = []
        for idx, current_slice in enumerate(slice_tuple):
            if isinstance(current_slice, slice):
                slice_list.append(self._check_for_string_slice_indices(current_slice, idx))
            else:
                if isinstance(current_slice, string_types):
                    slice_list.append(self._get_string_slice_index(current_slice, idx))
                else:
                    slice_list.append(current_slice)

        return self._tvb.data[tuple(slice_list)]

    @property
    def title(self):
        return self._tvb.title

    @property
    def data(self):
        return self._tvb.data

    @property
    def shape(self):
        return self._tvb.data.shape

    @property
    def time_length(self):
        return self._tvb.length_1d

    @property
    def number_of_labels(self):
        return self._tvb.length_2d

    @property
    def number_of_variables(self):
        return self._tvb.length_3d

    @property
    def number_of_samples(self):
        return self._tvb.length_4d

    @property
    def start_time(self):
        return self._tvb.start_time

    @property
    def sample_period(self):
        return self._tvb.sample_period

    @property
    def end_time(self):
        return self.start_time + (self.time_length - 1) * self.sample_period

    @property
    def duration(self):
        return self.end_time - self.start_time

    def configure_time(self):
        self._tvb.time = numpy.arange(self.start_time, self.end_time + self.sample_period, self.sample_period)
        return self

    @property
    def time_unit(self):
        return self._tvb.sample_period_unit

    @property
    def sample_period_unit(self):
        return self._tvb.sample_period_unit

    @property
    def sample_rate(self):
        return self._tvb.sample_rate

    def configure_sampling_frequency(self):
        if len(self._tvb.sample_period_unit) > 0 and self._tvb.sample_period_unit[0] == "m":
            self._tvb.sample_rate = 1000.0/self._tvb.sample_period

        else:
            self._tvb.sample_rate = 1.0/self._tvb.sample_period
        return self

    def configure_sample_rate(self):
        return self.configure_sampling_frequency()

    @property
    def space_labels(self):
        try:
            return self._tvb.get_space_labels
        except:
            return self._tvb.labels_dimensions.get(TimeseriesDimensions.SPACE.value, numpy.array([]))

    @property
    def variables_labels(self):
        return self._tvblabels_dimensions.get(TimeseriesDimensions.VARIABLES.value, numpy.array([]))

    @property
    def labels_dimensions(self):
        return self._tvb.labels_dimensions

    @property
    def labels_ordering(self):
        return self._tvb.labels_ordering

    @property
    def nr_dimensions(self):
        return self._tvb.nr_dimensions

    @property
    def number_of_dimensions(self):
        return self._tvb.nr_dimensions

    @property
    def sensors(self):
        return self._tvb.sensors

    @property
    def connectivity(self):
        return self._tvb.connectivity

    @property
    def region_mapping_volume(self):
        return self._tvb.region_mapping_volume

    @property
    def region_mapping(self):
        return self._tvb.region_mapping

    @property
    def surface(self):
        return self._tvb.surface

    @property
    def volume(self):
        return self._tvb.volume

    @property
    def squeezed(self):
        return numpy.squeeze(self._tvb.data)

    def _check_space_indices(self, list_of_index):
        for index in list_of_index:
            if index < 0 or index > self._tvb.data.shape[1]:
                self.logger.error("Some of the given indices are out of region range: [0, %s]",
                                  self._tvb.data.shape[1])
                raise IndexError

    def _get_time_unit_for_index(self, time_index):
        return self._tvb.start_time + time_index * self._tvb.sample_period

    def _get_index_for_time_unit(self, time_unit):
        return int((time_unit - self._tvb.start_time) / self._tvb.sample_period)

    def get_subspace_by_index(self, list_of_index, **kwargs):
        self._check_space_indices(list_of_index)
        subspace_data = self._tvb.data[:, list_of_index, :, :]
        subspace_labels_dimensions = deepcopy(self._tvb.labels_dimensions)
        subspace_labels_dimensions[TimeseriesDimensions.SPACE.value] = \
            numpy.array(self._tvb.labels_dimensions[TimeseriesDimensions.SPACE.value])[list_of_index]
        if subspace_data.ndim == 3:
            subspace_data = numpy.expand_dims(subspace_data, 1)
        return self.duplicate(data=subspace_data, labels_dimensions=subspace_labels_dimensions, **kwargs)

    def get_time_window(self, index_start, index_end, **kwargs):
        if index_start < 0 or index_end > self._tvb.data.shape[0]:
            self.logger.error("The time indices are outside time series interval: [%s, %s]" %
                              (0, self._tvb.data.shape[0]))
            raise IndexError
        subtime_data = self._tvb.data[index_start:index_end, :, :, :]
        if subtime_data.ndim == 3:
            subtime_data = numpy.expand_dims(subtime_data, 0)
        return self.duplicate(data=subtime_data, start_time=self._get_time_unit_for_index(index_start),  **kwargs)

    def get_time_window_by_units(self, unit_start, unit_end, **kwargs):
        end_time = self.end_time
        if unit_start < self._tvb.start_time or unit_end > end_time:
            self.logger.error("The time units are outside time series interval: [%s, %s]" %
                              (self._tvb.start_time, end_time))
            raise ValueError
        index_start = self._get_index_for_time_unit(unit_start)
        index_end = self._get_index_for_time_unit(unit_end)
        return self.get_time_window(index_start, index_end)

    def decimate_time(self, new_sample_period, **kwargs):
        if new_sample_period % self.sample_period != 0:
            self.logger.error("Cannot decimate time if new time step is not a multiple of the old time step")
            raise ValueError

        index_step = int(new_sample_period / self._tvb.sample_period)
        time_data = self._tvb.data[::index_step, :, :, :]
        return self.duplicate(data=time_data, sample_period=new_sample_period, **kwargs)

    def get_sample_window(self, index_start, index_end, **kwargs):
        subsample_data = self._tvb.data[:, :, :, index_start:index_end]
        if subsample_data.ndim == 3:
            subsample_data = numpy.expand_dims(subsample_data, 3)
        return self.duplicate(data=subsample_data, **kwargs)

    def get_source(self, **kwargs):
        if TimeseriesDimensions.VARIABLES.value not in self._tvb.labels_dimensions.keys():
            self.logger.error("No state variables are defined for this instance!")
            raise ValueError
        if PossibleVariables.SOURCE.value in self._tvb.labels_dimensions[TimeseriesDimensions.VARIABLES.value]:
            return self.get_state_variable(PossibleVariables.SOURCE.value)

    def get_bipolar(self, **kwargs):
        bipolar_labels, bipolar_inds = monopolar_to_bipolar(self.space_labels)
        data = self._tvb.data[:, bipolar_inds[0]] - self._tvb.data[:, bipolar_inds[1]]
        bipolar_labels_dimensions = deepcopy(self._tvb.labels_dimensions)
        bipolar_labels_dimensions["space"] = numpy.array(bipolar_labels)
        return self.duplicate(data=data, labels_dimensions=bipolar_labels_dimensions, **kwargs)

    def configure(self):
        self.configure_time()
        self.configure_sampling_frequency()
        self._tvb.configure()
        self.configure_sample_rate()
        return self

    def duplicate(self, **kwargs):
        duplicate = deepcopy(self)
        for attr, value in kwargs.items():
            setattr(duplicate, attr, value)
        return duplicate.configure()


if __name__ == "__main__":

    kwargs = {"data": numpy.ones((4, 2, 10, 1)), "start_time": 0.0, "ts_type": "Region"}
    ts = Timeseries(**kwargs)
    print(ts)