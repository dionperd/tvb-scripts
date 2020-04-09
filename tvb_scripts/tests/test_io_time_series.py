# coding=utf-8
import numpy
from tvb_scripts.tests.base import BaseTest
from tvb_scripts.datatypes.time_series import TimeSeriesRegion, TimeSeriesDimensions, PossibleVariables
from tvb_scripts.io.h5_writer import H5Writer, h5


class TestIOTimeseries(BaseTest):
    writer = H5Writer()

    def test_timeseries_4D(self):
        data, start_time, sample_period, sample_period_unit = self._prepare_dummy_time_series(4)
        ts = \
            TimeSeriesRegion(data,
                             labels_dimensions={TimeSeriesDimensions.SPACE.value: ["r1", "r2", "r3", "r4"],
                                                TimeSeriesDimensions.VARIABLES.value: [
                                                   PossibleVariables.X.value, PossibleVariables.Y.value,
                                                   PossibleVariables.Z.value]},
                             start_time=start_time, sample_period=sample_period,
                             sample_period_unit=sample_period_unit,
                             connectivity=self._prepare_connectivity())

        path = self.writer.write_tvb_to_h5(ts, recursive=True)
        ts2 = TimeSeriesRegion(h5.load_with_references(path))
        assert numpy.max(numpy.abs(ts.data - ts2.data)) < 1e-6
        assert numpy.all(ts.variables_labels == ts2.variables_labels) < 1e-6
        assert numpy.all(ts.space_labels == ts2.space_labels)
        assert numpy.abs(ts.start_time - ts2.start_time) < 1e-6
        assert numpy.abs(ts.sample_period - ts2.sample_period) < 1e-6
        assert numpy.all(ts.sample_period_unit == ts2.sample_period_unit)


if __name__ == "__main__":

    TestIOTimeseries().test_timeseries_4D()

