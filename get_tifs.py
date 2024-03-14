import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping

def download_and_save_geotiff(name, link, geojson_path):
    # Read GeoJSON
    gdf = gpd.read_file(geojson_path)

    # Open the original GeoTIFF
    with rasterio.open(link) as src:
        # Crop the GeoTIFF
        out_image, out_transform = mask(src, gdf.geometry, crop=True)
        out_meta = src.meta.copy()

        # Update metadata for the cropped GeoTIFF
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # Save the cropped GeoTIFF
        with rasterio.open(f"{name}.tif", "w", **out_meta) as dest:
            dest.write(out_image)

    print(f"Cropped GeoTIFF saved as {name}.tif")

# Define paths to input files
kenya_geojson_path = "kenya.geojson"  # Replace with the actual path to your Kenya GeoJSON file

# Download and save GeoTIFFs
download_and_save_geotiff("kenya_phosphorus", "https://files.isric.org/public/af250m_nutrient/af250m_nutrient_p_m_agg30cm.tif", kenya_geojson_path)
download_and_save_geotiff("kenya_potassium", "https://files.isric.org/public/af250m_nutrient/af250m_nutrient_k_m_agg30cm.tif", kenya_geojson_path)