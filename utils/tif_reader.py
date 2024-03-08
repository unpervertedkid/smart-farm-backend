import rasterio

def get_value_at_point(raster_file, lon, lat):
    # Open the raster file
    with rasterio.open(raster_file) as src:
        # Convert the point's coordinates to the raster's coordinate system
        row, col = src.index(lon, lat)
        
        # Read the raster's values at the point's location
        value = src.read(1)[row, col]
        
    return value


