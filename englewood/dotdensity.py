#!/usr/bin/env python

import os
import random
import shutil

from osgeo import gdal
from osgeo import ogr

gdal.UseExceptions()

class DotDensityPlotter(object):
    """
    Creates dot density maps (as shapefiles) from input boundaries
    and related data.
    """
    def __init__(self, source, dest, data_callback, dot_size, masks=[]):
        """
        Takes the name of a boundary shapefile directory, the name of an
        output directory, a callback to fetch data (takes an OGR Feature
        as an argument) and the number of units each dot should represent.
        """
        self.source = ogr.Open(source, False)
        self.source_layer = self.source.GetLayer(0)

        try:
            shutil.rmtree(dest)
        except OSError:
            pass

        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.dest = driver.CreateDataSource(dest)
        self.dest_layer = self.dest.CreateLayer('dot_density', geom_type=ogr.wkbPoint)

        group_field = ogr.FieldDefn('GROUP', ogr.OFTString) 
        self.dest_layer.CreateField(group_field)

        self.data_callback = data_callback
        self.dot_size = dot_size

        # If using masks, generate a masked version of the input shapes
        if masks:
            try:
                shutil.rmtree('temp_masked')
            except OSError:
                pass

            driver = ogr.GetDriverByName('ESRI Shapefile')
            masked = driver.CreateDataSource('temp_masked')
            masked_layer = masked.CreateLayer('temp_masked', geom_type=ogr.wkbMultiPolygon)
            
            for i in range(self.source_layer.GetLayerDefn().GetFieldCount()):
                masked_layer.CreateField(self.source_layer.GetLayerDefn().GetFieldDefn(i))

            mask_features = []

            for mask in masks:
                geo = ogr.Open(mask)
                layer = geo.GetLayer(0)

                for feature in layer:
                    mask_features.append(feature)

            for feature in self.source_layer:
                masked_feature = ogr.Feature(feature_def=self.source_layer.GetLayerDefn())
                masked_feature.SetFrom(feature)

                masked_geometry = feature.GetGeometryRef().Clone()

                for mask_feature in mask_features:
                    masked_geometry = masked_geometry.Difference(mask_feature.GetGeometryRef())
     
                masked_feature.SetGeometryDirectly(masked_geometry)
                masked_layer.CreateFeature(masked_feature)

            masked_layer.SyncToDisk()

            # Substitute masked shapes for input shapes
            self.source = masked
            self.source_layer = masked_layer
            self.source_layer.ResetReading()

    def _plot(self, feature):
        """
        Plots dots for a single feature in the source layer.
        """
        data = self.data_callback(feature)

        if not data:
            return

        dot_list = self.get_group_list(data, self.dot_size)

        for dot in dot_list:
            f = ogr.Feature(feature_def=self.dest_layer.GetLayerDefn())
            f.SetField("GROUP", dot)

            point = self.random_point_in_feature(feature)

            f.SetGeometryDirectly(point)
            self.dest_layer.CreateFeature(f)

            f.Destroy()

    def plot(self):
        """
        Plots dots for all features in the source layer.
        """
        feature = self.source_layer.GetNextFeature()

        while feature:
            self._plot(feature)

            feature = self.source_layer.GetNextFeature()

    @classmethod
    def random_point_in_feature(cls, feature):
        """
        Generate a random point within a feature polygon.
        """
        point = None

        while not point or not feature.GetGeometryRef().Contains(point):
            geometry = feature.GetGeometryRef()
            minx, maxx, miny, maxy = geometry.GetEnvelope()
            x = random.uniform(minx,maxx)
            y = random.uniform(miny,maxy)

            point = ogr.Geometry(ogr.wkbPoint)
            point.SetPoint(0, x, y)

        return point

    @classmethod  
    def get_group_list(cls, groups, divisor):
        """
        Convert a dict of group names and population sizes to a list, with a group name for every (size / divisor).

        Return the list shuffled to combat z-index bias.
        """
        group_list = []

        for group, count in groups.items():
            for x in range(count / divisor):
                group_list.append(group)

        random.shuffle(group_list)

        return group_list

