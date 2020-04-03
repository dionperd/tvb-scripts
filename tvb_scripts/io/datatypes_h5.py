# coding=utf-8

from tvb_scripts.datatypes.surface import Surface
from tvb_scripts.datatypes.head import Head

from tvb.core.neotraits.h5 import H5File, Scalar, DataSet, Reference
from tvb.adapters.datatypes.h5.region_mapping_h5 import *
from tvb.adapters.datatypes.h5.structural_h5 import *
from tvb.adapters.datatypes.h5.volumes_h5 import *
from tvb.adapters.datatypes.h5.surface_h5 import SurfaceH5 as TVBSurfaceH5
from tvb.adapters.datatypes.h5.projections_h5 import *
from tvb.adapters.datatypes.h5.time_series_h5 import *


# Surface


class SurfaceH5(TVBSurfaceH5):

    def __init__(self, path):
        super(SurfaceH5, self).__init__(path)
        self.vox2ras = DataSet(Surface.vox2ras, self)
        if not self.is_new_file:
            self._vox2ras = self.vox2ras.load()

    def store(self, datatype, scalars_only=False, store_references=True):
        super(SurfaceH5, self).store(datatype, scalars_only, store_references)
        self.vox2ras.store(self._vox2ras)


class HeadH5(H5File):

    def __init__(self, path):
        super(HeadH5, self).__init__(path)
        self.name = Scalar(Head.name, self)
        self.path = Scalar(Head.path, self)
        self.connectivity = Reference(Head.connectivity, self)
        self.volume = Reference(Head.volume, self)
        self.cortical_surface = Reference(Head.cortical_surface, self)
        self.subcortical_surface = Reference(Head.subcortical_surface, self)
        self.cortical_region_mapping = Reference(Head.cortical_region_mapping, self)
        self.subcortical_region_mapping = Reference(Head.subcortical_region_mapping, self)
        self.region_volume_mapping = Reference(Head.region_volume_mapping, self)
        self.sensorsEEG = Reference(Head.sensorsEEG, self)
        self.sensorsSEEG = Reference(Head.sensorsSEEG, self)
        self.sensorsMEG = Reference(Head.sensorsMEG, self)
        self.projectionEEG = Reference(Head.projectionEEG, self)
        self.projectionMEG = Reference(Head.projectionMEG, self)
        self.sensorsMEG = Reference(Head.sensorsMEG, self)
        self.t1 = Reference(Head.t1, self)
