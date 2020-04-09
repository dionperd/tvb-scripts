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

    def _prepare_connectivity(self):
        self.connectivity = Connectivity(weights=numpy.array([[0.0, 2.0, 3.0, 4.0],
                                                              [2.0, 0.0, 2.0, 3.0],
                                                              [3.0, 2.0, 0.0, 1.0],
                                                              [4.0, 3.0, 1.0, 0.0]]),
                                         tract_lengths=numpy.array([[0.0, 2.0, 3.0, 4.0],
                                                                    [2.0, 0.0, 2.0, 3.0],
                                                                    [3.0, 2.0, 0.0, 1.0],
                                                                    [4.0, 3.0, 1.0, 0.0]]),
                                         region_labels=numpy.array(["a", "b", "c", "d"]),
                                         centres=numpy.array([1.0, 2.0, 3.0, 4.0]),
                                         areas=numpy.array([1.0, 2.0, 3.0, 4.0]))
        return self.connectivity

    def _prepare_dummy_head_from_dummy_attrs(self):

        self._prepare_connectivity()

        self.surface = CorticalSurface(vertices=numpy.array([[1, 2, 3], [2, 3, 1], [3, 1, 2]]),
                                        triangles=numpy.array([[0, 1, 2]]))
        self.sensors = SensorsSEEG(labels=numpy.array(["sens1", "sens2", "sens3"]),
                                   locations=numpy.array([[0, 0, 0], [0, 1, 0], [0, 1, 1]]))
        self.projection = ProjectionSurfaceSEEG(projection_data=numpy.random.uniform(0, 1, (3, 4)))

        return Head(connectivity=self.connectivity,
                    cortical_surface=self.surface,
                    seeg_sensors=self.sensors,
                    seeg_projection=self.projection)

    def _prepare_dummy_head(self):
        head = Head.from_folder(self.config.input.HEAD, eeg_projection="ProjectionMatrix")  #
        head.configure()
        return head

    def _prepare_dummy_time_series(self, dim):
        if dim == 1:
            data = numpy.array([1, 2, 3, 4, 5])
        elif dim == 2:
            data = numpy.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])[:, numpy.newaxis, :]
        elif dim == 3:
            data = numpy.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9], [0, 1, 2]],
                               [[3, 4, 5], [6, 7, 8], [9, 0, 1], [2, 3, 4]],
                               [[5, 6, 7], [8, 9, 0], [1, 2, 3], [4, 5, 6]]])
        else:
            data = numpy.array([[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 0, 1, 2]],
                                [[3, 4, 5, 6], [7, 8, 9, 0], [1, 2, 3, 4]],
                                [[5, 6, 7, 8], [9, 0, 1, 2], [3, 4, 5, 6]],
                                [[7, 8, 9, 0], [1, 2, 3, 4], [5, 6, 7, 8]]],
                               [[[9, 0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 0]],
                                [[1, 2, 3, 4], [5, 6, 7, 8], [9, 0, 1, 2]],
                                [[3, 4, 5, 6], [7, 8, 9, 0], [1, 2, 3, 4]],
                                [[5, 6, 7, 8], [9, 0, 1, 2], [3, 4, 5, 6]]],
                               [[[7, 8, 9, 0], [1, 2, 3, 4], [5, 6, 7, 8]],
                                [[9, 0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 0]],
                                [[1, 2, 3, 4], [5, 6, 7, 8], [9, 0, 1, 2]],
                                [[3, 4, 5, 6], [7, 8, 9, 0], [1, 2, 3, 4]]]]).reshape((3, 3, 4, 4))
        start_time = 0
        sample_period = 0.01
        sample_period_unit = "ms"

        return data, start_time, sample_period, sample_period_unit

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
