# coding=utf-8

from tvb_scripts.datatypes.connectivity import Connectivity
from tvb_scripts.datatypes.local_connectivity import LocalConnectivity
from tvb_scripts.datatypes.surface import Surface, CorticalSurface, SubcorticalSurface
from tvb_scripts.datatypes.region_mapping import *
from tvb_scripts.datatypes.sensors import *
from tvb_scripts.datatypes.projections import *
from tvb_scripts.datatypes.structural import *
from tvb_scripts.datatypes.head import Head
from tvb_scripts.datatypes.time_series import *


from tvb.config.init.datatypes_registry import REGISTRY, populate_datatypes_registry
from tvb.core.neotraits.h5 import H5File, Scalar, DataSet, Reference
from tvb.adapters.datatypes.h5.connectivity_h5 import ConnectivityH5 as TVBConnectivityH5
from tvb.adapters.datatypes.h5.local_connectivity_h5 import LocalConnectivityH5 as TVBLocalConnectivityH5
from tvb.adapters.datatypes.h5.region_mapping_h5 import RegionMappingH5 as TVBRegionMappingH5
from tvb.adapters.datatypes.h5.region_mapping_h5 import RegionVolumeMappingH5 as TVBRegionVolumeMappingH5
from tvb.adapters.datatypes.h5.structural_h5 import StructuralMRIH5 as TVBStructuralMRIH5
from tvb.adapters.datatypes.h5.surface_h5 import SurfaceH5 as TVBSurfaceH5
from tvb.adapters.datatypes.h5.sensors_h5 import SensorsH5
from tvb.adapters.datatypes.h5.projections_h5 import ProjectionMatrixH5 as TVBProjectionMatrixH5
from tvb.adapters.datatypes.h5.time_series_h5 import *
from tvb.adapters.datatypes.db.connectivity import ConnectivityIndex
from tvb.adapters.datatypes.db.local_connectivity import LocalConnectivityIndex
from tvb.adapters.datatypes.db.surface import SurfaceIndex
from tvb.adapters.datatypes.db.region_mapping import RegionMappingIndex, RegionVolumeMappingIndex
from tvb.adapters.datatypes.db.structural import StructuralMRIIndex
from tvb.adapters.datatypes.db.sensors import SensorsIndex
from tvb.adapters.datatypes.db.projections import ProjectionMatrixIndex
from tvb.adapters.datatypes.db.time_series import *


class ConnectivityH5(TVBConnectivityH5):
    pass


class LocalConnectivityH5(TVBLocalConnectivityH5):
    pass


class SurfaceH5(TVBSurfaceH5):

    def __init__(self, path):
        super(SurfaceH5, self).__init__(path)
        self.vox2ras = DataSet(Surface.vox2ras, self)

    def store(self, datatype, scalars_only=False, store_references=True):
        super(SurfaceH5, self).store(datatype, scalars_only, store_references)


class CorticalSurfaceH5(SurfaceH5):

    def __init__(self, path):
        super(CorticalSurfaceH5, self).__init__(path)
        self.vox2ras = DataSet(CorticalSurface.vox2ras, self)


class SubcorticalSurfaceH5(SurfaceH5):

    def __init__(self, path):
        super(SubcorticalSurfaceH5, self).__init__(path)
        self.vox2ras = DataSet(SubcorticalSurface.vox2ras, self)


class RegionMappingH5(TVBRegionMappingH5):
    pass


class CorticalRegionMappingH5(RegionMappingH5):
    pass


class SubcorticalRegionMappingH5(RegionMappingH5):
    pass


class RegionVolumeMappingH5(TVBRegionVolumeMappingH5):
    pass


class StructuralMRIH5(TVBStructuralMRIH5):
    pass


class T1H5(StructuralMRIH5):
    pass


class T2H5(StructuralMRIH5):
    pass

class FlairH5(StructuralMRIH5):
    pass


class B0H5(StructuralMRIH5):
    pass


class SensorsEEGH5(SensorsH5):
    pass


class SensorsSEEGH5(SensorsH5):
    pass


class SensorsMEGH5(SensorsH5):
    pass


class SensorsInternalH5(SensorsH5):
    pass


class ProjectionMatrixH5(TVBProjectionMatrixH5):
    pass


class ProjectionSurfaceEEGH5(TVBProjectionMatrixH5):
    pass


class ProjectionSurfaceSEEGH5(TVBProjectionMatrixH5):
    pass


class ProjectionSurfaceMEGH5(TVBProjectionMatrixH5):
    pass


class HeadH5(H5File):

    def __init__(self, path):
        super(HeadH5, self).__init__(path)
        self.title = Scalar(Head.title, self)
        self.path = Scalar(Head.path, self)
        self.connectivity = Reference(Head.connectivity, self)
        self.cortical_surface = Reference(Head.cortical_surface, self)
        self.subcortical_surface = Reference(Head.subcortical_surface, self)
        self.cortical_region_mapping = Reference(Head.cortical_region_mapping, self)
        self.subcortical_region_mapping = Reference(Head.subcortical_region_mapping, self)
        self.region_volume_mapping = Reference(Head.region_volume_mapping, self)
        self.t1 = Reference(Head.t1, self)
        self.t2 = Reference(Head.t2, self)
        self.flair = Reference(Head.flair, self)
        self.b0 = Reference(Head.b0, self)
        self.eeg_sensors = Reference(Head.eeg_sensors, self)
        self.seeg_sensors = Reference(Head.seeg_sensors, self)
        self.meg_sensors = Reference(Head.meg_sensors, self)
        self.eeg_projection = Reference(Head.eeg_projection, self)
        self.meg_projection = Reference(Head.meg_projection, self)
        self.meg_sensors = Reference(Head.meg_sensors, self)


populate_datatypes_registry()

REGISTRY.register_datatype(Connectivity, ConnectivityH5, ConnectivityIndex)
REGISTRY.register_datatype(LocalConnectivity, LocalConnectivityH5, LocalConnectivityIndex)
REGISTRY.register_datatype(Surface, SurfaceH5, SurfaceIndex)
REGISTRY.register_datatype(CorticalSurface, CorticalSurfaceH5, SurfaceIndex)
REGISTRY.register_datatype(SubcorticalSurface, SubcorticalSurfaceH5, SurfaceIndex)
REGISTRY.register_datatype(Surface, RegionMappingH5, RegionMappingIndex)
REGISTRY.register_datatype(CorticalRegionMapping, CorticalRegionMappingH5, RegionMappingIndex)
REGISTRY.register_datatype(SubcorticalRegionMapping, SubcorticalRegionMappingH5, RegionMappingIndex)
REGISTRY.register_datatype(RegionVolumeMapping, RegionVolumeMappingH5, RegionVolumeMappingIndex)
REGISTRY.register_datatype(StructuralMRI, StructuralMRIH5, StructuralMRIIndex)
REGISTRY.register_datatype(T1, T1H5, StructuralMRIIndex)
REGISTRY.register_datatype(T2, T2H5, StructuralMRIIndex)
REGISTRY.register_datatype(Flair, FlairH5, StructuralMRIIndex)
REGISTRY.register_datatype(B0, B0H5, StructuralMRIIndex)
REGISTRY.register_datatype(Sensors, SensorsH5, SensorsIndex)
REGISTRY.register_datatype(SensorsEEG, SensorsEEGH5, SensorsIndex)
REGISTRY.register_datatype(SensorsSEEG, SensorsSEEGH5, SensorsIndex)
REGISTRY.register_datatype(SensorsInternal, SensorsInternalH5, SensorsIndex)
REGISTRY.register_datatype(SensorsMEG, SensorsMEGH5, SensorsIndex)
REGISTRY.register_datatype(ProjectionMatrix, ProjectionMatrixH5, ProjectionMatrixIndex)
REGISTRY.register_datatype(ProjectionSurfaceEEG, ProjectionSurfaceEEGH5, ProjectionMatrixIndex)
REGISTRY.register_datatype(ProjectionSurfaceSEEG, ProjectionSurfaceSEEGH5, ProjectionMatrixIndex)
REGISTRY.register_datatype(ProjectionSurfaceMEG, ProjectionSurfaceMEGH5, ProjectionMatrixIndex)
REGISTRY.register_datatype(TimeSeries, TimeSeriesH5, TimeSeriesIndex)
REGISTRY.register_datatype(TimeSeriesRegion, TimeSeriesRegionH5, TimeSeriesRegionIndex)
REGISTRY.register_datatype(TimeSeriesSurface, TimeSeriesSurfaceH5, TimeSeriesSurfaceIndex)
REGISTRY.register_datatype(TimeSeriesVolume, TimeSeriesVolumeH5, TimeSeriesVolumeIndex)
REGISTRY.register_datatype(TimeSeriesEEG, TimeSeriesEEGH5, TimeSeriesEEGIndex)
REGISTRY.register_datatype(TimeSeriesMEG, TimeSeriesMEGH5, TimeSeriesMEGIndex)
REGISTRY.register_datatype(TimeSeriesSEEG, TimeSeriesSEEGH5, TimeSeriesSEEGIndex)
REGISTRY.register_datatype(Head, HeadH5, None)
