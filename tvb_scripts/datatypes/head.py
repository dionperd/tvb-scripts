# coding=utf-8

from collections import OrderedDict

from tvb_scripts.utils.log_error_utils import initialize_logger
from tvb_scripts.datatypes.surface import CorticalSurface, SubcorticalSurface
from tvb_scripts.datatypes.sensors import *

from tvb.datatypes.connectivity import Connectivity as TVBConnectivity
from tvb.datatypes.region_mapping import *
from tvb.datatypes.structural import StructuralMRI
from tvb.datatypes.surfaces import Surface as TVBSurface
from tvb.datatypes.cortex import Cortex
from tvb.datatypes.sensors import Sensors as TVBSensors
from tvb.datatypes.projections import ProjectionMatrix
from tvb.basic.neotraits.api import HasTraits, List, Attr


class Head(HasTraits):
    """
    One patient virtualization. Fully configured for defining hypothesis on it.
    """
    logger = initialize_logger(__name__)
    title = Attr(str, default="Virtual Head")
    path = Attr(str, default="path", required=False)
    connectivity = Attr(field_type=Connectivity)
    cortical_surface = Attr(field_type=CorticalSurface, required=False)
    subcortical_surface = Attr(field_type=SubcorticalSurface, required=False)
    cortical_region_mapping = Attr(field_type=RegionMapping, required=False)
    subcortical_region_mapping = Attr(field_type=RegionMapping, required=False)
    region_volume_mapping = Attr(field_type=RegionVolumeMapping, required=False)
    t1 = Attr(field_type=StructuralMRI, required=False)
    sensorsEEG = List(of=SensorsEEG, default=[], required=False)
    sensorsSEEG = List(of=SensorsEEG, default=[], required=False)
    sensorsMEG = List(of=SensorsEEG, default=[], required=False)
    projectionEEG = List(of=ProjectionMatrix, default=[], required=False)
    projectionSEEG = List(of=ProjectionMatrix, default=[], required=False)
    projectionMEG = List(of=ProjectionMatrix, default=[], required=False)

    def __init__(self, **kwargs):
        super(Head, self).__init__(**kwargs)
        self.sensors_dict = OrderedDict(zip(self.sensors, self.projections))

    @property
    def number_of_regions(self):
        return self.connectivity.number_of_regions

    @property
    def cortex(self):
        cortex = Cortex()
        cortex.region_mapping_data = self.cortical_region_mapping
        cortex = cortex.populate_cortex(self.cortical_surface._tvb, {})
        for s_type, sensors in self.sensors_dict.items():
            if isinstance(sensors, OrderedDict) and len(sensors) > 0:
                projection = sensors.values()[0]
                if projection is not None:
                    setattr(cortex, s_type.lower(), projection.projection_data)
        cortex.configure()
        return cortex

    def configure(self):
        if isinstance(self.connectivity, TVBConnectivity):
            self.connectivity.configure()
        if isinstance(self.cortical_surface, TVBSurface):
            self.cortical_surface.configure()
        if isinstance(self.subcortical_surface, TVBSurface):
            self.subcortical_surface.configure()
        if isinstance(self.cortical_region_mapping, RegionMapping):
            self.cortical_region_mapping.configure()
        if isinstance(self.subcortical_region_mapping, RegionMapping):
            self.subcortical_region_mapping.configure()
        if isinstance(self.region_volume_mapping, RegionVolumeMapping):
            self.region_volume_mapping.configure()
        if isinstance(self.t1, StructuralMRI):
            self.t1.configure()
        for s_type in ["EEG", "SEEG", "MEG"]:
            sensor =  "sensors%s" % s_type
            if isinstance(getattr(self, sensor), TVBSensors):
                getattr(self, sensor).configure()
                projection = "projection%s" % s_type
                if isinstance(getattr(self, projection), ProjectionMatrix):
                        getattr(self, projection).configure()
        self.sensors_dict = OrderedDict(zip(self.sensors, self.projections))

    def filter_regions(self, filter_arr):
        return self.connectivity.region_labels[filter_arr]
