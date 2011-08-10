#!/usr/bin/env python

import random

from osgeo import gdal
from osgeo import ogr

gdal.UseExceptions()

class DotDensityPlotter(object):
    """
    Creates dot density maps (as shapefiles) from input boundaries
    and related data.
    """
    def __init__(self, source, source_layer, dest_driver, dest, dest_layer, data_callback, dot_size, masks=[]):
        """
        Takes the name of a boundary shapefile directory, the name of an
        output directory, a callback to fetch data (takes an OGR Feature
        as an argument) and the number of units each dot should represent.
        """
        self.source = ogr.Open(source, False)
        self.source_layer = self.source.GetLayerByName(source_layer)

        driver = ogr.GetDriverByName(dest_driver)
        self.dest = driver.CreateDataSource(dest)

        try:
            self.dest.DeleteLayer(dest_layer)
        except ValueError:
            pass

        self.dest_layer = self.dest.CreateLayer(dest_layer, geom_type=ogr.wkbPoint)

        group_field = ogr.FieldDefn('GROUP', ogr.OFTString) 
        self.dest_layer.CreateField(group_field)

        self.data_callback = data_callback
        self.dot_size = dot_size

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
        for feature in self.source_layer:
            self._plot(feature)

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

