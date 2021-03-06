# -*- coding: utf-8 -*-
import os
from tvb_scripts.utils.file_utils import delete_all_files_in_folder
from tvb_scripts.plot.plotter import Plotter
from tvb_scripts.tests.base import BaseTest


class TestPlotter(BaseTest):
    plotter = Plotter(BaseTest.config)

    def test_plot_head(self):
        head = self._prepare_dummy_head_from_dummy_attrs()
        # TODO: this filenames may change because they are composed inside the plotting functions
        filename1 = "Connectivity.png"
        filename2 = "HeadStats.png"
        filename3 = "SEEG-Projection.png"

        delete_all_files_in_folder(self.config.out.FOLDER_FIGURES)

        assert not os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename1))
        assert not os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename2))
        assert not os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename3))

        self.plotter.plot_head(head, plot_stats=True, plot_sensors=True)

        assert os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename1))
        assert os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename2))
        # Because there is no gain matrix
        assert not os.path.exists(os.path.join(self.config.out.FOLDER_FIGURES, filename3))


if __name__ == "__main__":
    TestPlotter().test_plot_head()
