# coding=utf-8
from enum import Enum

import numpy as np

from tvb_utils.log_error_utils import warning
from tvb_utils.data_structures_utils import reg_dict, formal_repr, sort_dict, ensure_list, \
    labels_to_inds, monopolar_to_bipolar, split_string_text_numbers


class SensorTypes(Enum):
    TYPE_EEG = 'EEG'
    TYPE_MEG = "MEG"
    TYPE_SEEG = "SEEG"


class SensorsH5Field(object):
    GAIN_MATRIX = "gain_matrix"
    LABELS = "labels"
    LOCATIONS = "locations"


class Sensors(object):

    s_type = SensorTypes.TYPE_EEG
    name = s_type.value
    labels = np.array([])
    locations = np.array([])
    gain_matrix = np.array([])

    def __init__(self, labels, locations, gain_matrix=np.array([]),
                 s_type=SensorTypes.TYPE_SEEG, name=SensorTypes.TYPE_EEG.value, remove_leading_zeros_from_labels=True):
        self.name = name
        self.labels = labels
        self.locations = locations
        self.gain_matrix = gain_matrix
        self.s_type = s_type
        self.elec_labels = self.labels
        self.elec_inds = np.array(range(len(self.number_of_sensors)))
        if len(self.labels) > 1 and self.s_type == SensorTypes.TYPE_SEEG.value:
            self.elec_labels, self.elec_inds = self.group_sensors_to_electrodes()
        if remove_leading_zeros_from_labels:
            self.remove_leading_zeros_from_labels()

    @property
    def number_of_sensors(self):
        return self.locations.shape[0]

    @property
    def number_of_electrodes(self):
        return self.group_sensors_to_electrodes()[0].size

    @property
    def channel_labels(self):
        return self.elec_labels

    @property
    def channel_inds(self):
        return self.elec_inds

    def __repr__(self):
        d = {"1. sensors' type": self.s_type,
             "2. number of sensors": self.number_of_sensors,
             "3. labels": reg_dict(self.labels),
             "4. locations": reg_dict(self.locations, self.labels),
             "5. gain_matrix": self.gain_matrix}
        return formal_repr(self, sort_dict(d))

    def __str__(self):
        return self.__repr__()

    def sensor_label_to_index(self, labels):
        indexes = []
        for label in ensure_list(labels):
            indexes.append(np.where([np.array(lbl) == np.array(label) for lbl in self.labels])[0][0])
        if isinstance(labels, (list, tuple)) or len(indexes) > 1:
            return indexes
        else:
            return indexes[0]

    def get_sensors_inds_by_sensors_labels(self, lbls):
        # Make sure that the labels are not bipolar:
        lbls = [label.split("-")[0] for label in ensure_list(lbls)]
        return labels_to_inds(self.labels, lbls)

    def get_elecs_inds_by_elecs_labels(self, lbls):
        return labels_to_inds(self.elec_labels, lbls)

    def get_sensors_inds_by_elec_labels(self, lbls):
        elec_inds = self.get_elecs_inds_by_elecs_labels(lbls)
        sensors_inds = []
        for ind in elec_inds:
            sensors_inds += self.elec_inds[ind]
        return np.unique(sensors_inds)

    def group_sensors_to_electrodes(self, labels=None):
        if self.s_type == SensorTypes.TYPE_SEEG:
            if labels is None:
                labels = self.labels
            sensor_names = np.array(split_string_text_numbers(labels))
            elec_labels = np.unique(sensor_names[:, 0])
            elec_inds = []
            for chlbl in elec_labels:
                elec_inds.append(np.where(sensor_names[:, 0] == chlbl)[0])
            return elec_labels, elec_inds
        else:
            warning("No multisensor electrodes for %s sensors!" % self.s_type)
            return self.elec_labels, self.elec_inds

    def remove_leading_zeros_from_labels(self):
        labels = []
        for label in self.labels:
            elec_name, sensor_ind = split_string_text_numbers(label)[0]
            labels.append(elec_name + sensor_ind.lstrip("0"))
        self.labels = np.array(labels)

    def get_bipolar_sensors(self, sensors_inds=None):
        if sensors_inds is None:
            sensors_inds = range(self.number_of_sensors)
        return monopolar_to_bipolar(self.labels, sensors_inds)

    def get_bipolar_elecs(self, elecs):
        try:
            bipolar_sensors_lbls = []
            bipolar_sensors_inds = []
            for elec_ind in elecs:
                curr_inds, curr_lbls = self.get_bipolar_sensors(sensors_inds=self.elec_inds[elec_ind])
                bipolar_sensors_inds.append(curr_inds)
                bipolar_sensors_lbls.append(curr_lbls)
        except:
            elecs_inds = self.get_elecs_inds_by_elecs_labels(elecs)
            bipolar_sensors_inds, bipolar_sensors_lbls = self.get_bipolar_elecs(elecs_inds)
        return bipolar_sensors_inds, bipolar_sensors_lbls
