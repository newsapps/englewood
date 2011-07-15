#!/usr/bin/env python

import random
import shutil

from osgeo import ogr

class DotDensityPlotter(object):
    """
    Creates dot density maps (as shapefiles) from input boundaries
    and related data.
    """
    def __init__(self, source, dest, data_callback, dot_size):
        """
        Takes the name of a boundary shapefile directory, the name of an
        output directory, a callback to fetch data (takes an OGR Feature
        as an argument) and the number of units each dot should represent.
        """
        self.source = ogr.Open(source)
        self.source_layer = self.source.GetLayer(0)

        shutil.rmtree(dest)

        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.dest = driver.CreateDataSource(dest)
        self.dest_layer = self.dest.CreateLayer('dot_density', geom_type=ogr.wkbPoint)

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
        feature = self.source_layer.GetNextFeature()

        while feature:
            self._plot(feature)

            feature = self.source_layer.GetNextFeature()

        self.source.Destroy()
        self.dest.Destroy()

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
            
            wkt = "POINT(%f %f)" % (x,y)
            point = ogr.CreateGeometryFromWkt(wkt)

        return point

