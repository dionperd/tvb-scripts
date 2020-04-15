# -*- coding: utf-8 -*-
import numpy as np
from tvb_scripts.io.h5_writer import H5Writer
from tvb_scripts.tests.base import BaseTest, Head


class TestIOHead(BaseTest):
    writer = H5Writer()

    def test_read_head_folder_and_write_h5(self):
        head = self._prepare_dummy_head()
        path = self.writer.write_tvb_to_h5(head, recursive=True)

        head2 = Head.from_file(path)
        assert np.max(np.abs(head.connectivity.weights - head2.connectivity.weights)) < 1e-6
        assert np.max(np.abs(head.connectivity.tract_lengths - head2.connectivity.tract_lengths)) < 1e-6
        assert np.max(np.abs(head.surface.vertices - head2.surface.vertices)) < 1e-6
        assert np.max(np.abs(head.surface.triangles - head2.surface.triangles)) < 1e-6
        assert np.max(np.abs(head.eeg_sensors.locations - head2.eeg_sensors.locations)) < 1e-6
        assert np.max(np.abs(head.eeg_projection.projection_data - head2.eeg_projection.projection_data)) < 1e-6

        # The following will not work as long as Head references tvb-scripts classes instead of TVB ones
        from tvb.core.neocom import h5
        head3 = h5.load(path, with_references=True)
        assert np.max(np.abs(head.connectivity.weights - head3.connectivity.weights)) < 1e-6
        assert np.max(np.abs(head.connectivity.tract_lengths - head3.connectivity.tract_lengths)) < 1e-6
        assert np.max(np.abs(head.surface.vertices - head3.surface.vertices)) < 1e-6
        assert np.max(np.abs(head.surface.triangles - head3.surface.triangles)) < 1e-6
        assert np.max(np.abs(head.eeg_sensors.locations - head3.eeg_sensors.locations)) < 1e-6
        assert np.max(np.abs(head.eeg_projection.projection_data - head3.eeg_projection.projection_data)) < 1e-6


if __name__ == "__main__":
    TestIOHead().test_read_head_folder_and_write_h5()
