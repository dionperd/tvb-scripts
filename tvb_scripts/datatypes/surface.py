# coding=utf-8

import numpy as np

from tvb_scripts.datatypes.base import BaseModel
from tvb.basic.neotraits.api import NArray, Attr
from tvb.datatypes.surfaces import Surface as TVBSurface
from tvb.datatypes.surfaces import WhiteMatterSurface as TVBWhiteMatterSurface
from tvb.datatypes.surfaces import CorticalSurface as TVBCorticalSurface
from tvb.datatypes.surfaces import SkinAir as TVBSkinAir
from tvb.datatypes.surfaces import BrainSkull as TVBBrainSkull
from tvb.datatypes.surfaces import SkullSkin as TVBSkullSkin
from tvb.datatypes.surfaces import EEGCap as TVBEEGCap
from tvb.datatypes.surfaces import FaceSurface as TVBFaceSurface


class Surface(TVBSurface, BaseModel):

    vox2ras = NArray(
        dtype=np.float,
        label="vox2ras", default=np.array([]), required=False,
        doc="""Voxel to RAS coordinates transformation array.""")

    def get_vertex_normals(self):
        # If there is at least 3 vertices and 1 triangle...
        if self.number_of_vertices > 2 and self.number_of_triangles > 0:
            if self.vertex_normals.shape[0] != self.number_of_vertices:
                self.vertex_normals = self.compute_vertex_normals()
        return self.vertex_normals

    def get_triangle_normals(self):
        # If there is at least 3 vertices and 1 triangle...
        if self.number_of_vertices > 2 and self.number_of_triangles > 0:
            if self.triangle_normals.shape[0] != self.number_of_triangles:
                self.triangle_normals = self.compute_triangle_normals()
        return self.triangle_normals

    def get_vertex_areas(self):
        triangle_areas = self._find_triangle_areas()
        vertex_areas = np.zeros((self.number_of_vertices,))
        for triang, vertices in enumerate(self.triangles):
            for i in range(3):
                vertex_areas[vertices[i]] += 1. / 3. * triangle_areas[triang]
        return vertex_areas

    def add_vertices_and_triangles(self, new_vertices, new_triangles,
                                   new_vertex_normals=np.array([]),  new_triangle_normals=np.array([])):
        self.triangles = np.array(self.triangles.tolist() +
                                       (new_triangles + self.number_of_vertices).tolist())
        self.vertices = np.array(self.vertices.tolist() + new_vertices.tolist())
        self.vertex_normals = np.array(self.vertex_normals.tolist() + new_vertex_normals.tolist())
        self.triangle_normals = np.array(self.triangle_normals.tolist() + new_triangle_normals.tolist())
        self.get_vertex_normals()
        self.get_triangle_normals()

    def compute_surface_area(self):
        """
            This function computes the surface area
            :param: surface: input surface object
            :return: (sub)surface area, float
            """
        return np.sum(self._find_triangle_areas())

    def configure(self):
        try:
            self.zero_based_triangles
        except:
            self.zero_based_triangles = False
        super(Surface, self).configure()

    def to_tvb_instance(self, datatype=TVBSurface, **kwargs):
        return super(Surface, self).to_tvb_instance(datatype, **kwargs)


class WhiteMatterSurface(Surface, TVBWhiteMatterSurface):

    def to_tvb_instance(self, **kwargs):
        return super(WhiteMatterSurface, self).to_tvb_instance(TVBWhiteMatterSurface, **kwargs)


class CorticalSurface(Surface, TVBCorticalSurface):

    def to_tvb_instance(self, **kwargs):
        return super(CorticalSurface, self).to_tvb_instance(TVBCorticalSurface, **kwargs)


class SubcorticalSurface(Surface, TVBCorticalSurface):

    surface_type = Attr(field_type=str, default="Subcortical Surface")

    def to_tvb_instance(self, **kwargs):
        return super(SubcorticalSurface, self).to_tvb_instance(TVBCorticalSurface, **kwargs)


class SkinAirSurface(Surface, TVBSkinAir):

    def to_tvb_instance(self, **kwargs):
        return super(SkinAirSurface, self).to_tvb_instance(TVBSkinAir, **kwargs)


class BrainSkullSurface(Surface, TVBBrainSkull):

    def to_tvb_instance(self, **kwargs):
        return super(BrainSkullSurface, self).to_tvb_instance(TVBBrainSkull, **kwargs)


class SkullSkinSurface(Surface, TVBSkullSkin):

    def to_tvb_instance(self, **kwargs):
        return super(SkullSkinSurface, self).to_tvb_instance(TVBSkullSkin, **kwargs)


class EEGCapSurface(Surface, TVBEEGCap):

    def to_tvb_instance(self, **kwargs):
        return super(EEGCapSurface, self).to_tvb_instance(TVBEEGCap, **kwargs)


class FaceSurfaceSurface(Surface, TVBFaceSurface):

    def to_tvb_instance(self, **kwargs):
        return super(FaceSurfaceSurface, self).to_tvb_instance(TVBFaceSurface, **kwargs)
