# -*- coding: utf-8 -*-

import os
import h5py
from collections import OrderedDict

import numpy as np

from tvb_scripts.utils.log_error_utils import initialize_logger, raise_value_error
from tvb_scripts.utils.data_structures_utils import isequal_string
from tvb_scripts.virtual_head.connectivity import Connectivity, ConnectivityH5Field
from tvb_scripts.virtual_head.head import Head
from tvb_scripts.virtual_head.sensors import \
    Sensors, SensorTypesToClassesDict, SensorsH5Field, SensorTypesToProjectionDict
from tvb_scripts.virtual_head.surface import CorticalSurface, SubcorticalSurface, SurfaceH5Field
from tvb_scripts.time_series.model import LABELS_ORDERING, TimeSeries
from tvb_scripts.io.h5_writer import H5Writer

from tvb.datatypes import region_mapping, structural
from tvb.datatypes.projections import ProjectionMatrix


H5_TYPE_ATTRIBUTE = H5Writer().H5_TYPE_ATTRIBUTE
H5_SUBTYPE_ATTRIBUTE = H5Writer().H5_SUBTYPE_ATTRIBUTE
H5_TYPES_ATTRUBUTES = [H5_TYPE_ATTRIBUTE, H5_SUBTYPE_ATTRIBUTE]


class H5Reader(object):
    logger = initialize_logger(__name__)

    connectivity_filename = "Connectivity.h5"
    cortical_surface_filename = "CorticalSurface.h5"
    subcortical_surface_filename = "SubcorticalSurface.h5"
    cortical_region_mapping_filename = "RegionMapping.h5"
    subcortical_region_mapping_filename = "RegionMappingSubcortical.h5"
    volume_mapping_filename = "VolumeMapping.h5"
    structural_mri_filename = "StructuralMRI.h5"
    sensors_filename_prefix = "Sensors"
    sensors_filename_separator = "_"

    def read_connectivity(self, path):
        """
        :param path: Path towards a custom Connectivity H5 file
        :return: Connectivity object
        """
        self.logger.info("Starting to read a Connectivity from: %s" % path)
        if os.path.isfile(path):
            h5_file = h5py.File(path, 'r', libver='latest')

            weights = h5_file['/' + ConnectivityH5Field.WEIGHTS][()]
            try:
                tract_lengths = h5_file['/' + ConnectivityH5Field.TRACTS][()]
            except:
                tract_lengths = np.array([])
            try:
                region_centres = h5_file['/' + ConnectivityH5Field.CENTERS][()]
            except:
                region_centres = np.array([])
            try:
                region_labels = h5_file['/' + ConnectivityH5Field.REGION_LABELS][()]
            except:
                region_labels = np.array([])
            try:
                orientations = h5_file['/' + ConnectivityH5Field.ORIENTATIONS][()]
            except:
                orientations = np.array([])
            try:
                hemispheres = h5_file['/' + ConnectivityH5Field.HEMISPHERES][()]
            except:
                hemispheres = np.array([])
            try:
                areas = h5_file['/' + ConnectivityH5Field.AREAS][()]
            except:
                areas = np.array([])

            h5_file.close()

            conn = Connectivity(file_path=path, weights=weights, tract_lengths=tract_lengths,
                                region_labels=region_labels, region_centres=region_centres,
                                hemispheres=hemispheres, orientations=orientations, areas=areas)
            conn.configure()
            self.logger.info("Successfully read connectvity from: %s" % path)

            return conn
        else:
            raise_value_error(("\n No Connectivity file found at path %s!" % str(path)))

    def read_surface(self, path, surface_class):
        """
        :param path: Path towards a custom Surface H5 file
        :return: Surface object
        """
        if not os.path.isfile(path):
            self.logger.warning("Surface file %s does not exist" % path)
            return None

        self.logger.info("Starting to read Surface from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        vertices = h5_file['/' + SurfaceH5Field.VERTICES][()]
        triangles = h5_file['/' + SurfaceH5Field.TRIANGLES][()]
        try:
            vertex_normals = h5_file['/' + SurfaceH5Field.VERTEX_NORMALS][()]
        except:
            vertex_normals = np.array([])
        try:
            triangle_normals = h5_file['/' + SurfaceH5Field.TRIANGLE_NORMALS][()]
        except:
            triangle_normals = np.array([])
        h5_file.close()

        surface = surface_class(file_path=path, vertices=vertices, triangles=triangles,
                                vertex_normals=vertex_normals, triangle_normals=triangle_normals)
        surface.configure()

        self.logger.info("Successfully read surface from: %s" % path)

        return surface

    def read_sensors(self, path):
        """
        :param path: Path towards a custom virtual_head folder
        :return: 3 lists with all sensors from Path by type
        """
        sensors = OrderedDict()

        self.logger.info("Starting to read all Sensors from: %s" % path)

        all_head_files = os.listdir(path)
        for head_file in all_head_files:
            str_head_file = str(head_file)
            if not str_head_file.startswith(self.sensors_filename_prefix):
                continue
            name = str_head_file.split(".")[0]
            sensor, projection = \
                self.read_sensors_of_type(os.path.join(path, head_file), name)
            sensors_set = sensors.get(sensor.sensors_type, OrderedDict())
            sensors_set.update({sensor: projection})
            sensors[sensor.sensors_type] = sensors_set

        self.logger.info("Successfuly read all sensors from: %s" % path)

        return sensors

    def read_sensors_of_type(self, sensors_file, name):
        """
        :param
            sensors_file: Path towards a custom Sensors H5 file
            s_type: Senors s_type
        :return: Sensors object
        """
        if not os.path.exists(sensors_file):
            self.logger.warning("Senors file %s does not exist!" % sensors_file)
            return []

        self.logger.info("Starting to read sensors of from: %s" % sensors_file)
        h5_file = h5py.File(sensors_file, 'r', libver='latest')

        locations = h5_file['/' + SensorsH5Field.LOCATIONS][()]
        try:
            labels = h5_file['/' + SensorsH5Field.LABELS][()]
        except:
            labels = np.array([])
        try:
            orientations = h5_file['/' + SensorsH5Field.ORIENTATIONS][()]
        except:
            orientations = np.array([])
        name = h5_file.attrs.get("name", name)
        s_type = h5_file.attrs.get("Sensors_subtype", "")

        if '/' + SensorsH5Field.PROJECTION_MATRIX in h5_file:
            proj_matrix = h5_file['/' + SensorsH5Field.PROJECTION_MATRIX][()]
            projection = SensorTypesToProjectionDict.get(s_type, ProjectionMatrix())()
            projection.projection_data = proj_matrix
        else:
            projection = None

        h5_file.close()

        sensors = \
            SensorTypesToClassesDict.get(s_type, Sensors)(file_path=sensors_file, name=name,
                                                          labels=labels, locations=locations,
                                                          orientations=orientations)
        sensors.configure()
        self.logger.info("Successfully read sensors from: %s" % sensors_file)

        return sensors, projection

    def read_volume_mapping(self, path):
        """
        :param path: Path towards a custom VolumeMapping H5 file
        :return: volume mapping in a numpy array
        """
        if not os.path.isfile(path):
            self.logger.warning("VolumeMapping file %s does not exist" % path)
            return None

        self.logger.info("Starting to read VolumeMapping from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        vm = region_mapping.RegionVolumeMapping()
        vm.array_data = h5_file['/data'][()]

        h5_file.close()
        self.logger.info("Successfully read volume mapping!")  #: %s" % data)

        return vm

    def read_region_mapping(self, path):
        """
        :param path: Path towards a custom RegionMapping H5 file
        :return: region mapping in a numpy array
        """
        if not os.path.isfile(path):
            self.logger.warning("RegionMapping file %s does not exist" % path)
            return None

        self.logger.info("Starting to read RegionMapping from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        rm = region_mapping.RegionMapping()
        rm.array_data = h5_file['/data'][()]

        h5_file.close()
        self.logger.info("Successfully read region mapping!")  #: %s" % data)

        return rm

    def read_t1(self, path):
        """
        :param path: Path towards a custom StructuralMRI H5 file
        :return: structural MRI in a numpy array
        """
        if not os.path.isfile(path):
            self.logger.warning("StructuralMRI file %s does not exist" % path)
            return None

        self.logger.info("Starting to read StructuralMRI from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        t1 = structural.StructuralMRI()
        t1.array_data = h5_file['/data'][()]

        h5_file.close()
        self.logger.info("Successfully read structural MRI from: %s" % path)

        return t1

    def read_head(self, path, atlas="default"):
        """
        :param path: Path towards a custom virtual_head folder
        :return: Head object
        """
        self.logger.info("Starting to read Head from: %s" % path)
        conn = \
            self.read_connectivity(os.path.join(path, self.connectivity_filename))
        cort_srf =\
            self.read_surface(os.path.join(path, self.cortical_surface_filename), CorticalSurface)
        subcort_srf = \
            self.read_surface(os.path.join(path, self.subcortical_surface_filename), SubcorticalSurface)
        cort_rm = \
            self.read_region_mapping(os.path.join(path, self.cortical_region_mapping_filename))
        if cort_rm is not None:
            cort_rm.connectivity = conn._tvb
            if cort_srf is not None:
                cort_rm.surface = cort_srf._tvb
        subcort_rm = \
            self.read_region_mapping(os.path.join(path, self.subcortical_region_mapping_filename))
        if subcort_rm is not None:
            subcort_rm.connectivity = conn._tvb
            if subcort_srf is not None:
                subcort_rm.surface = subcort_srf._tvb
        vm = \
            self.read_volume_mapping(os.path.join(path, self.volume_mapping_filename))
        t1 = \
            self.read_t1(os.path.join(path, self.structural_mri_filename))
        sensors = self.read_sensors(path)

        if len(atlas) > 0:
            name = atlas
        else:
            name = path

        head = Head(conn, sensors, cort_srf, subcort_srf, cort_rm, subcort_rm, vm, t1, name)

        self.logger.info("Successfully read Head from: %s" % path)

        return head

    def read_ts(self, path):
        """
        :param path: Path towards a valid TimeSeries H5 file
        :return: Timeseries data and time in 2 numpy arrays
        """
        self.logger.info("Starting to read TimeSeries from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        data = h5_file['/data'][()]
        total_time = int(h5_file["/"].attrs["Simulated_period"][0])
        nr_of_steps = int(h5_file["/data"].attrs["Number_of_steps"][0])
        start_time = float(h5_file["/data"].attrs["Start_time"][0])
        time = np.linspace(start_time, total_time, nr_of_steps)

        self.logger.info("First Channel sv sum: " + str(np.sum(data[:, 0])))
        self.logger.info("Successfully read timeseries!")  #: %s" % data)
        h5_file.close()

        return time, data

    def read_timeseries(self, path, timeseries=TimeSeries):
        """
        :param path: Path towards a valid TimeSeries H5 file
        :return: Timeseries data and time in 2 numpy arrays
        """
        self.logger.info("Starting to read TimeSeries from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')

        data = h5_file['/data'][()]

        ts_kwargs = {}
        labels_dimensions = {}
        try:
            time = h5_file['/time'][()]
            ts_kwargs["time"] = time
            ts_kwargs["sample_period"] = float(np.mean(np.diff(time)))
        except:
            pass
        try:
            labels_ordering = (h5_file['/dimensions_labels'][()]).tolist()
        except:
            labels_ordering = LABELS_ORDERING
        try:
            labels_dimensions.update({labels_ordering[2]: h5_file['/labels'][()]})
        except:
            pass
        try:
            labels_dimensions.update({labels_ordering[1]: h5_file['/variables'][()]})
        except:
            pass
        if len(labels_dimensions) > 0:
            ts_kwargs["labels_dimensions"] = labels_dimensions
        time_unit = str(h5_file.attrs.get("sample_period_unit", ""))
        if len(time_unit) > 0:
            ts_kwargs["sample_period_unit"] = time_unit
        ts_type = str(h5_file.attrs.get("time_series_type", ""))
        if len(ts_type) > 0:
            ts_kwargs["ts_type"] = ts_type
        title = str(h5_file.attrs.get("title", ""))
        if len(title) > 0:
            ts_kwargs["title"] = title
        self.logger.info("First Channel sv sum: " + str(np.sum(data[:, 0])))
        self.logger.info("Successfully read Timeseries!")  #: %s" % data)
        h5_file.close()

        return timeseries(data, labels_ordering=labels_ordering, **ts_kwargs)

    def read_dictionary(self, path, type=None):
        """
        :param path: Path towards a dictionary H5 file
        :return: dict
        """
        self.logger.info("Starting to read a dictionary from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')
        dictionary = H5GroupHandlers().read_dictionary_from_group(h5_file, type)
        h5_file.close()
        return dictionary

    def read_list_of_dicts(self, path, type=None):
        self.logger.info("Starting to read a list of dictionaries from: %s" % path)
        h5_file = h5py.File(path, 'r', libver='latest')
        list_of_dicts = []
        id = 0
        h5_group_handlers = H5GroupHandlers()
        while 1:
            try:
                dict_group = h5_file[str(id)]
            except:
                break
            list_of_dicts.append(h5_group_handlers.read_dictionary_from_group(dict_group, type))
            id += 1
        h5_file.close()
        return list_of_dicts


class H5GroupHandlers(object):

    def read_dictionary_from_group(self, group, type=None):
        dictionary = dict()
        for dataset in group.keys():
            dictionary.update({dataset: group[dataset][()]})
        for attr in group.attrs.keys():
            dictionary.update({attr: group.attrs[attr]})
        if type is None:
            type = group.attrs[H5_SUBTYPE_ATTRIBUTE]
        else:
            return dictionary
