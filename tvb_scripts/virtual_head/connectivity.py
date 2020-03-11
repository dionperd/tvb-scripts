# coding=utf-8
import numpy as np
from tvb_scripts.utils.data_structures_utils import labels_to_inds
from tvb_scripts.virtual_head.base import BaseModel
from tvb.datatypes.connectivity import Connectivity as TVBConnectivity


class ConnectivityH5Field(object):
    WEIGHTS = "weights"
    TRACTS = "tract_lengths"
    CENTERS = "centres"
    CENTRES = "centres"
    REGION_LABELS = "region_labels"
    ORIENTATIONS = "orientations"
    HEMISPHERES = "hemispheres"
    AREAS = "areas"


class Connectivity(TVBConnectivity, BaseModel):
    file_path = ""

    def __setattr__(self, key, value):
        if key == "centers":
            super(Connectivity, self).__setattr__("centres", value)
        else:
            super(Connectivity, self).__setattr__(key, value)

    @classmethod
    def from_file(cls, filepath, **kwargs):
        result = cls.from_tvb_instance(cls.from_file(filepath), **kwargs)
        result.file_path = filepath
        return result

    @property
    def centers(self):
        return self.centres

    @property
    def number_of_regions(self):
        return self._tvb.weights.shape[0]

    def regions_labels2inds(self, labels):
        inds = []
        for lbl in labels:
            inds.append(np.where(self.region_labels == lbl)[0][0])
        if len(inds) == 1:
            return inds[0]
        else:
            return inds

    def get_regions_inds_by_labels(self, lbls):
        return labels_to_inds(self.region_labels, lbls)
