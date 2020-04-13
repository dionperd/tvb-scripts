# -*- coding: utf-8 -*-

import os
import numpy
from datetime import datetime

from tvb.basic.profile import TvbProfile

TvbProfile.set_profile(TvbProfile.LIBRARY_PROFILE)


class GenericConfig(object):
    _module_path = os.path.dirname(__file__)

    # Identify and choose the Simulator, or data folder type to read.
    MODE_H5 = "H5"
    MODE_TVB = "TVB"


class InputConfig(object):
    _base_input = os.getcwd()

    @property
    def HEAD(self):
        if self._head_folder is not None:
            return self._head_folder

        # or else, try to find tvb_data module
        try:
            import tvb_data
            # TODO: Create a default example Head in tvb-data
            return os.path.join(os.path.dirname(tvb_data.__file__), "berlinSubjects", "QL_20120814")
        except ImportError:
            return self._base_input

    @property
    def IS_TVB_MODE(self):
        """Identify and choose the Input data type to use"""
        return self._data_mode == GenericConfig.MODE_TVB

    @property
    def RAW_DATA_FOLDER(self):
        if self._raw_data is not None:
            return self._raw_data

        return os.path.join(self._base_input, "data", "raw")

    def __init__(self, head_folder=None, raw_folder=None, data_mode=GenericConfig.MODE_TVB):
        self._head_folder = head_folder
        self._raw_data = raw_folder
        self._data_mode = data_mode


class OutputConfig(object):
    subfolder = None

    def __init__(self, out_base=None, separate_by_run=False):
        """
        :param work_folder: Base folder where logs/figures/results should be kept
        :param separate_by_run: Set TRUE, when you want logs/results/figures to be in different files / each run
        """
        self._out_base = out_base or os.path.join(os.getcwd(), "outputs")
        self._separate_by_run = separate_by_run

    @property
    def FOLDER_LOGS(self):
        folder = os.path.join(self._out_base, "logs")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M')
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        return folder

    @property
    def FOLDER_RES(self):
        folder = os.path.join(self._out_base, "res")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M')
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        if self.subfolder is not None:
            os.path.join(folder, self.subfolder)
        return folder

    @property
    def FOLDER_FIGURES(self):
        folder = os.path.join(self._out_base, "figs")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M')
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        if self.subfolder is not None:
            os.path.join(folder, self.subfolder)
        return folder

    @property
    def FOLDER_TEMP(self):
        return os.path.join(self._out_base, "temp")


class FiguresConfig(object):
    VERY_LARGE_SIZE = (40, 20)
    VERY_LARGE_PORTRAIT = (30, 50)
    SUPER_LARGE_SIZE = (80, 40)
    LARGE_SIZE = (20, 15)
    SMALL_SIZE = (15, 10)
    NOTEBOOK_SIZE = (20, 10)
    FIG_FORMAT = 'png'
    SAVE_FLAG = True
    SHOW_FLAG = False
    MOUSE_HOOVER = False
    MATPLOTLIB_BACKEND = "Agg"  # "Qt4Agg"
    WEIGHTS_NORM_PERCENT = 99
    FONTSIZE = 10
    SMALL_FONTSIZE = 8
    LARGE_FONTSIZE = 12

    def largest_size(self):
        import sys
        if 'IPython' not in sys.modules:
            return self.LARGE_SIZE
        from IPython import get_ipython
        if getattr(get_ipython(), 'kernel', None) is not None:
            return self.NOTEBOOK_SIZE
        else:
            return self.LARGE_SIZE

    def __init__(self, out_base=None, separate_by_run=False):
        """
        :param out_base: Base folder where figures should be kept
        :param separate_by_run: Set TRUE, when you want figures to be in different files / each run
        """
        self._out_base = out_base or TvbProfile.current.TVB_STORAGE or os.path.join(os.getcwd(), "outputs")
        self._separate_by_run = separate_by_run

    @property
    def FOLDER_FIGURES(self):
        folder = os.path.join(self._out_base, "figs")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M')
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        return folder


class CalculusConfig(object):
    # Normalization configuration
    WEIGHTS_NORM_PERCENT = 99

    # If True a plot will be generated to choose the number of eigenvalues to keep
    INTERACTIVE_ELBOW_POINT = False

    MIN_SINGLE_VALUE = numpy.finfo("single").min
    MAX_SINGLE_VALUE = numpy.finfo("single").max
    MAX_INT_VALUE = numpy.iinfo(numpy.int64).max
    MIN_INT_VALUE = numpy.iinfo(numpy.int64).max


class Config(object):
    generic = GenericConfig()
    figures = FiguresConfig()
    calcul = CalculusConfig()

    def __init__(self, head_folder=None, raw_data_folder=None, output_base=None, separate_by_run=False):
        self.input = InputConfig(head_folder, raw_data_folder)
        self.out = OutputConfig(output_base, separate_by_run)
        self.figures = FiguresConfig(output_base, separate_by_run)


CONFIGURED = Config()
