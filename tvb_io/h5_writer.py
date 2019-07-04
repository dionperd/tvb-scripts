# -*- coding: utf-8 -*-

import os
import h5py
import numpy
from tvb_utils.log_error_utils import raise_value_error
from tvb_utils.file_utils import change_filename_or_overwrite, write_metadata
from tvb_head.model.connectivity import ConnectivityH5Field
from tvb_head.model.sensors import SensorsH5Field, SensorTypes, Sensors
from tvb_head.model.surface import SurfaceH5Field, Surface
from tvb_timeseries.timeseries import Timeseries
from tvb_io.h5_writer_base import H5WriterBase

from tvb.datatypes.projections import ProjectionMatrix
from tvb.datatypes.region_mapping import RegionMapping, RegionVolumeMapping
from tvb.datatypes.structural import StructuralMRI


KEY_TYPE = "Type"
KEY_VERSION = "Version"
KEY_DATE = "Last_update"
KEY_NODES = "Number_of_nodes"
KEY_SENSORS = "Number_of_sensors"
KEY_MAX = "Max_value"
KEY_MIN = "Min_value"
KEY_CHANNELS = "Number_of_channels"
KEY_SV = "Number_of_state_variables"
KEY_STEPS = "Number_of_steps"
KEY_SAMPLING = "Sampling_period"
KEY_START = "Start_time"


class H5Writer(H5WriterBase):

    # TODO: write variants.
    def write_connectivity(self, connectivity, path):
        """
        :param connectivity: Connectivity object to be written in H5
        :param path: H5 path to be written
        """
        h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')

        h5_file.create_dataset(ConnectivityH5Field.WEIGHTS, data=connectivity.weights)
        h5_file.create_dataset(ConnectivityH5Field.TRACTS, data=connectivity.tract_lengths)
        h5_file.create_dataset(ConnectivityH5Field.CENTERS, data=connectivity.centres)
        h5_file.create_dataset(ConnectivityH5Field.REGION_LABELS, data=connectivity.region_labels)
        h5_file.create_dataset(ConnectivityH5Field.ORIENTATIONS, data=connectivity.orientations)
        h5_file.create_dataset(ConnectivityH5Field.HEMISPHERES, data=connectivity.hemispheres)
        h5_file.create_dataset(ConnectivityH5Field.AREAS, data=connectivity.areas)

        h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "Connectivity")
        h5_file.attrs.create("Number_of_regions", str(connectivity.number_of_regions))

        if connectivity.normalized_weights.size > 0:
            dataset = h5_file.create_dataset("normalized_weights/" + ConnectivityH5Field.WEIGHTS,
                                             data=connectivity.normalized_weights)
            dataset.attrs.create("Operations", "Removing diagonal, normalizing with 95th percentile, and ceiling to it")

        self.logger.info("Connectivity has been written to file: %s" % path)
        h5_file.close()

    def write_sensors(self, sensors, path, projection=None):
        """
        :param sensors: Sensors object to write in H5
        :param path: H5 path to be written
        """
        if isinstance(sensors, Sensors):
            h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')

            h5_file.create_dataset(SensorsH5Field.LABELS, data=sensors.labels)
            h5_file.create_dataset(SensorsH5Field.LOCATIONS, data=sensors.locations)
            h5_file.create_dataset(SensorsH5Field.ORIENTATIONS, data=sensors.orientations)

            if sensors.sensors_type in [SensorTypes.TYPE_SEEG.value, SensorTypes.TYPE_INTERNAL.value]:
                h5_file.create_dataset("ElectrodeLabels", data=sensors.channel_labels)
                h5_file.create_dataset("ElectrodeIndices", data=sensors.channel_inds)

            if isinstance(projection, ProjectionMatrix):
                projection = projection.projection_data
            elif not isinstance(projection, numpy.ndarray):
                projection = numpy.array([])
            projection_dataset = h5_file.create_dataset(SensorsH5Field.PROJECTION_MATRIX, data=projection)
            if projection.size > 0:
                projection_dataset.attrs.create("Max", str(projection.max()))
                projection_dataset.attrs.create("Min", str(projection.min()))

            h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "Sensors")
            h5_file.attrs.create("Number_of_sensors", str(sensors.number_of_sensors))
            h5_file.attrs.create("Sensors_subtype", str(sensors.sensors_type))
            h5_file.attrs.create("name", str(sensors.name))

            self.logger.info("Sensors have been written to file: %s" % path)
            h5_file.close()

    def write_surface(self, surface, path):
        """
        :param surface: Surface object to write in H5
        :param path: H5 path to be written
        """
        if isinstance(surface, Surface):
            h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')

            h5_file.create_dataset(SurfaceH5Field.VERTICES, data=surface.vertices)
            h5_file.create_dataset(SurfaceH5Field.TRIANGLES, data=surface.triangles)
            h5_file.create_dataset(SurfaceH5Field.VERTEX_NORMALS, data=surface.vertex_normals)
            h5_file.create_dataset(SurfaceH5Field.TRIANGLE_NORMALS, data=surface.triangle_normals)

            h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "Surface")
            h5_file.attrs.create("Surface_subtype", surface.surface_subtype.upper())
            h5_file.attrs.create("Number_of_triangles", surface.triangles.shape[0])
            h5_file.attrs.create("Number_of_vertices", surface.vertices.shape[0])
            h5_file.attrs.create("Voxel_to_ras_matrix", str(surface.vox2ras.flatten().tolist())[1:-1].replace(",", ""))

            self.logger.info("Surface has been written to file: %s" % path)
            h5_file.close()

    def write_region_mapping(self, region_mapping, path, n_regions, subtype="Cortical"):
        """
            :param region_mapping: region_mapping array to write in H5
            :param path: H5 path to be written
        """
        if isinstance(region_mapping, RegionMapping):
            h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')

            h5_file.create_dataset("data", data=region_mapping.array_data)

            data_length = len(region_mapping.array_data)
            h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "RegionMapping")
            h5_file.attrs.create("Connectivity_parcel", "Connectivity-%d" % n_regions)
            h5_file.attrs.create("Surface_parcel", "Surface-%s-%d" % (subtype.capitalize(), data_length))
            h5_file.attrs.create("Length_data", data_length)

            self.logger.info("Region mapping has been written to file: %s" % path)
            h5_file.close()

    def write_volume(self, volume, path, vol_type, n_regions):
        """
            :param t1: t1 array to write in H5
            :param path: H5 path to be written
        """
        if isinstance(volume, (RegionVolumeMapping, StructuralMRI)):
            shape = volume.array_data.shape
            if len(shape) < 3:
                shape = (0, 0, 0)
            h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')
            h5_file.create_dataset("data", data=volume.array_data)
            h5_file.attrs.create("Connectivity_parcel", "Connectivity-%d" % n_regions)
            h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "VolumeData")
            h5_file.attrs.create("Length_x", str(shape[0]))
            h5_file.attrs.create("Length_y", str(shape[1]))
            h5_file.attrs.create("Length_z", str(shape[2]))
            h5_file.attrs.create("Type", vol_type.upper())

            self.logger.info("%s volume has been written to file: %s" % (vol_type, path))
            h5_file.close()

    def write_t1(self, t1, path, n_regions):
        if isinstance(t1, StructuralMRI):
            self.write_volume(t1, path, "STRUCTURAL", n_regions)

    def write_volume_mapping(self, volume_mapping, path, n_regions):
        if isinstance(volume_mapping, RegionVolumeMapping):
            self.write_volume(volume_mapping, path, "MAPPING", n_regions)

    def write_head(self, head, path):
        """
        :param head: Head object to be written
        :param path: path to head folder
        """
        self.logger.info("Starting to write Head folder: %s" % path)

        if not (os.path.isdir(path)):
            os.mkdir(path)
        n_regions = head.connectivity.number_of_regions
        self.write_connectivity(head.connectivity, os.path.join(path, "Connectivity.h5"))
        self.write_surface(head.cortical_surface, os.path.join(path, "CorticalSurface.h5"))
        self.write_region_mapping(head.cortical_region_mapping, os.path.join(path, "CorticalRegionMapping.h5"),
                                  n_regions=n_regions, subtype="Cortical")
        if head.subcortical_surface is not None:
            self.write_surface(head.subcortical_surface, os.path.join(path, "SubcorticalSurface.h5"))
            self.write_region_mapping(head.subcortical_region_mapping,
                                      os.path.join(path, "SubcorticalRegionMapping.h5"),
                                      n_regions, "Subcortical")
        self.write_volume_mapping(head.region_volume_mapping, os.path.join(path, "VolumeMapping.h5"), n_regions)
        self.write_t1(head.t1, os.path.join(path, "StructuralMRI.h5"), n_regions)
        for s_type, sensors_set in head.sensors.items():
            for sensor, projection in sensors_set.items():
                self.write_sensors(sensor,
                                   os.path.join(path, "%s.h5" % sensor.name.replace(" ", "")),
                                   projection)

        self.logger.info("Successfully wrote Head folder at: %s" % path)

    def write_dictionary_to_group(self, dictionary, group):
        group.attrs.create(self.H5_TYPE_ATTRIBUTE, "HypothesisModel")
        group.attrs.create(self.H5_SUBTYPE_ATTRIBUTE, dictionary.__class__.__name__)
        for key, value in dictionary.items():
            try:
                if isinstance(value, numpy.ndarray) and value.size > 0:
                    group.create_dataset(key, data=value)
                else:
                    if isinstance(value, list) and len(value) > 0:
                        group.create_dataset(key, data=value)
                    else:
                        group.attrs.create(key, value)
            except:
                self.logger.warning("Did not manage to write " + key + " to h5 file " + str(group) + " !")

    def write_dictionary(self, dictionary, path):
        """
        :param dictionary: dictionary to write in H5
        :param path: H5 path to be written
        """
        self.logger.info("Writing a dictionary at:\n" + path)
        h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')
        self.write_dictionary_to_group(dictionary, h5_file)
        h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "HypothesisModel")
        h5_file.attrs.create(self.H5_SUBTYPE_ATTRIBUTE, dictionary.__class__.__name__)
        h5_file.close()

    def write_list_of_dictionaries(self, list_of_dicts, path):
        self.logger.info("Writing a list of dictionaries at:\n" + path)
        h5_file = h5py.File(change_filename_or_overwrite(path), 'a', libver='latest')
        for idict, dictionary in enumerate(list_of_dicts):
            idict_str = str(idict)
            h5_file.create_group(idict_str)
            self.write_dictionary_to_group(dictionary, h5_file[idict_str])
        h5_file.attrs.create(self.H5_TYPE_ATTRIBUTE, "HypothesisModel")
        h5_file.attrs.create(self.H5_SUBTYPE_ATTRIBUTE, "list")
        h5_file.close()

    def write_ts(self, raw_data, sampling_period, path):
        path = change_filename_or_overwrite(path)

        self.logger.info("Writing a TS at:\n" + path)
        h5_file = h5py.File(path, 'a', libver='latest')
        write_metadata({KEY_TYPE: "TimeSeries"}, h5_file, KEY_DATE, KEY_VERSION)
        if isinstance(raw_data, dict):
            for data in raw_data:
                if len(raw_data[data].shape) == 2 and str(raw_data[data].dtype)[0] == "f":
                    h5_file.create_dataset("/" + data, data=raw_data[data])
                    write_metadata({KEY_MAX: raw_data[data].max(), KEY_MIN: raw_data[data].min(),
                                    KEY_STEPS: raw_data[data].shape[0], KEY_CHANNELS: raw_data[data].shape[1],
                                    KEY_SV: 1, KEY_SAMPLING: sampling_period, KEY_START: 0.0}, h5_file, KEY_DATE,
                                   KEY_VERSION, "/" + data)
                else:
                    raise_value_error("Invalid TS data. 2D (time, nodes) numpy.ndarray of floats expected")
        elif isinstance(raw_data, numpy.ndarray):
            if len(raw_data.shape) != 2 and str(raw_data.dtype)[0] != "f":
                h5_file.create_dataset("/data", data=raw_data)
                write_metadata({KEY_MAX: raw_data.max(), KEY_MIN: raw_data.min(), KEY_STEPS: raw_data.shape[0],
                                KEY_CHANNELS: raw_data.shape[1], KEY_SV: 1, KEY_SAMPLING: sampling_period,
                                KEY_START: 0.0}, h5_file, KEY_DATE, KEY_VERSION, "/data")
            else:
                raise_value_error("Invalid TS data. 2D (time, nodes) numpy.ndarray of floats expected")
        elif isinstance(raw_data, Timeseries):
            if len(raw_data.shape) == 4 and str(raw_data.data.dtype)[0] == "f":
                h5_file.create_dataset("/data", data=raw_data.data)
                h5_file.create_dataset("/time", data=raw_data.time)
                h5_file.create_dataset("/labels",
                                       data=numpy.array([numpy.string_(label) for label in raw_data.space_labels]))
                h5_file.create_dataset("/variables",
                                       data=numpy.array([numpy.string_(var) for var in raw_data.variables_labels]))
                h5_file.attrs.create("time_unit", raw_data.time_unit)
                write_metadata({KEY_MAX: raw_data.data.max(), KEY_MIN: raw_data.data.min(),
                                KEY_STEPS: raw_data.data.shape[0], KEY_CHANNELS: raw_data.data.shape[1],
                                KEY_SV: 1, KEY_SAMPLING: raw_data.time_step,
                                KEY_START: raw_data.time_start}, h5_file, KEY_DATE, KEY_VERSION, "/data")
            else:
                raise_value_error("Invalid TS data. 4D (time, nodes) numpy.ndarray of floats expected")
        else:
            raise_value_error("Invalid TS data. Dictionary or 2D (time, nodes) numpy.ndarray of floats expected")
        h5_file.close()

    def write_timeseries(self, timeseries, path):
        self.write_ts(timeseries, timeseries.time_step, path)
