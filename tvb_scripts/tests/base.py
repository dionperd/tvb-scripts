# -*- coding: utf-8 -*-

import os
import numpy
from tvb_scripts.config import Config
from tvb_scripts.datatypes.connectivity import Connectivity
from tvb_scripts.datatypes.surface import CorticalSurface
from tvb_scripts.datatypes.sensors import SensorsSEEG
from tvb_scripts.datatypes.projections import ProjectionSurfaceSEEG
from tvb_scripts.datatypes.head import Head


class BaseTest(object):
    config = Config(output_base=os.path.join(os.getcwd(), "test_out"))

    dummy_connectivity = Connectivity(weights=numpy.array([[1.0, 2.0, 3.0], [2.0, 3.0, 1.0], [3.0, 2.0, 1.0]]),
                                      tract_lengths=numpy.array([[4, 5, 6], [5, 6, 4], [6, 4, 5]]),
                                      region_labels=numpy.array(["a", "b", "c"]),
                                      centres=numpy.array([1.0, 2.0, 3.0]),
                                      areas=numpy.array([1.0, 2.0, 3.0]))
    dummy_surface = CorticalSurface(vertices=numpy.array([[1, 2, 3], [2, 3, 1], [3, 1, 2]]), triangles=numpy.array([[0, 1, 2]]))
    dummy_sensors = SensorsSEEG(labels=numpy.array(["sens1", "sens2"]), locations=numpy.array([[0, 0, 0], [0, 1, 0]]))
    dummy_projection = ProjectionSurfaceSEEG(projection_data=numpy.random.uniform(0, 1, (2, 3)))

    def _prepare_dummy_head_from_dummy_attrs(self):
        return Head(connectivity=self.dummy_connectivity,
                    cortical_surface=self.dummy_surface,
                    seeg_sensors=self.dummy_sensors,
                    seeg_projection=self.dummy_projection)

    def _prepare_dummy_head(self):
        head = Head.from_folder(self.config.input.HEAD, eeg_projection="ProjectionMatrix")  #
        head.configure()
        return head

    @classmethod
    def setup_class(cls):
        for direc in (cls.config.out.FOLDER_LOGS, cls.config.out.FOLDER_RES, cls.config.out.FOLDER_FIGURES,
                      cls.config.out.FOLDER_TEMP):
            if not os.path.exists(direc):
                os.makedirs(direc)

    @classmethod
    def teardown_class(cls):
        for direc in (cls.config.out.FOLDER_LOGS, cls.config.out.FOLDER_RES, cls.config.out.FOLDER_FIGURES,
                      cls.config.out.FOLDER_TEMP):
            for dir_file in os.listdir(direc):
                os.remove(os.path.join(os.path.abspath(direc), dir_file))
            os.removedirs(direc)
