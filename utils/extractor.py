import geopandas as gpd
import rasterio
from rasterio.mask import mask

# Load the GeoJSON file
kenya = gpd.read_file('kenya.geojson')

# Ensure it's using the same CRS as your raster file
kenya = kenya.to_crs({'init': 'epsg:4326'})

# Load the raster file
with rasterio.open('af250m_nutrient_k_m_agg30cm.tif') as src:
    # Crop the raster file using the GeoJSON
    out_image, out_transform = mask(src, kenya.geometry, crop=True)
    out_meta = src.meta.copy()

# Update the metadata
out_meta.update({
    "driver": "GTiff",
    "height": out_image.shape[1],
    "width": out_image.shape[2],
    "transform": out_transform,
})

# Save the resulting raster
with rasterio.open('phosphorus.tif', "w", **out_meta) as dest:
    dest.write(out_image)
