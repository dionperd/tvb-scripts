# coding=utf-8

from tvb.core.neotraits.h5 import DataSet
from tvb.adapters.datatypes.h5.connectivity_h5 import *
from tvb.adapters.datatypes.h5.region_mapping_h5 import *
from tvb.adapters.datatypes.h5.structural_h5 import *
from tvb.adapters.datatypes.h5.volumes_h5 import *
from tvb.adapters.datatypes.h5.surface_h5 import SurfaceH5 as TVBSurfaceH5
from tvb.adapters.datatypes.h5.sensors_h5 import *
from tvb.adapters.datatypes.h5.projections_h5 import *
from tvb.adapters.datatypes.h5.time_series_h5 import *
from tvb_scripts.datatypes.surface import Surface


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
