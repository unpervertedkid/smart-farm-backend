import rasterio

def get_value_at_point(raster_file, lon, lat):
    # Open the raster file
    with rasterio.open(raster_file) as src:
        # Convert the point's coordinates to the raster's coordinate system
        row, col = src.index(lon, lat)
        
        # Read the raster's values at the point's location
        value = src.read(1)[row, col]
        
    return value

# Test the function
lon = 36.817223  # replace with your longitude
lat = 1.286389  # replace with your latitude
raster_file = 'phosphorus.tif'  # replace with your raster file path

value = get_value_at_point(raster_file, lon, lat)
print(f'The value at point ({lon}, {lat}) is {value}')
