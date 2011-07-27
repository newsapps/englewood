#!/usr/bin/env python

import shutil

from osgeo import gdal
from osgeo import ogr

gdal.UseExceptions()

def mask(source_name, dest_name, masks=[]):
    """
    Masks a shapefile by "knocking out" the shapes from a list
    of other shapefiles. Maintains attribute data.
    """
    source = ogr.Open(source_name, False)
    source_layer = source.GetLayer(0)

    try:
        shutil.rmtree(dest_name)
    except OSError:
        pass

    driver = ogr.GetDriverByName('ESRI Shapefile')
    dest = driver.CreateDataSource(dest_name)
    dest_layer = dest.CreateLayer('masked', geom_type=ogr.wkbMultiPolygon)
    
    for i in range(source_layer.GetLayerDefn().GetFieldCount()):
        dest_layer.CreateField(source_layer.GetLayerDefn().GetFieldDefn(i))

    mask_features = []

    for mask in masks:
        geo = ogr.Open(mask)
        layer = geo.GetLayer(0)

        for feature in layer:
            mask_features.append(feature)

    for feature in source_layer:
        masked_feature = ogr.Feature(feature_def=source_layer.GetLayerDefn())
        masked_feature.SetFrom(feature)

        masked_geometry = feature.GetGeometryRef().Clone()

        for mask_feature in mask_features:
            masked_geometry = masked_geometry.Difference(mask_feature.GetGeometryRef())

        masked_feature.SetGeometryDirectly(masked_geometry)
        dest_layer.CreateFeature(masked_feature)
    
