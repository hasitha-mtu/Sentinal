import os
import os.path
import re
from datetime import date

import rasterio
import rasterio.mask
import rasterio.merge
from rasterio.plot import show

from pprint import pprint
import matplotlib.pyplot as plt

from utils import get_parent_directories
import glob


def select_files(path, pattern):
    L = []
    for root, dirs, files in os.walk(path):
        if len(dirs) == 0:
            for f in files:
                if re.match(pattern, f):
                    L.append(os.path.join(root, f))
    return L


def convert_to_tiff(paths):
    tiff_paths = []
    for p in paths:
        print("Converting " + p)
        with rasterio.open(p, mode="r") as src:
            profile = src.meta.copy()
            profile.update(driver="GTiff")

            outfile = re.sub(".jp2", ".tiff", p)
            with rasterio.open(outfile, 'w', **profile) as dst:
                dst.write(src.read())
                tiff_paths.append(outfile)
    return tiff_paths

def convert(DL_DIR):
    """
    Converting the .jp2 images to .tiff
    """
    jp2_paths = select_files(DL_DIR, "T*.*m.jp2$")
    tiff_paths = convert_to_tiff(jp2_paths)
    return tiff_paths

def merge(tiff_paths, output_file, DEBUG):
    """
    We're mergin the raster images.
    """

    raster_list = [rasterio.open(f, mode='r', driver="GTiff") for f in tiff_paths]
    merged_data, out_trans = rasterio.merge.merge(raster_list)

    if DEBUG:
        fig, ax = plt.subplots(figsize=(14, 14))
        show(merged_data, cmap='terrain', ax=ax)
        plt.show()

    merged_meta = raster_list[0].meta.copy()
    print(f"merged_meta : {merged_meta}")
    merged_meta.update({"driver": "GTiff",
                            "height": merged_data.shape[1],
                            "width": merged_data.shape[2],
                            "transform": out_trans,
                            "crs": raster_list[0].crs
                            # "count": 3,
                            })
    if DEBUG:
        for x in [x.meta for x in raster_list] + [merged_meta]:
            pprint(x)

    with rasterio.open(output_file, mode="w", **merged_meta) as dest:
        dest.write(merged_data)

def convert_jp2_to_tiff(path):
    print("Converting " + path)
    with rasterio.open(path, mode="r") as src:
        profile = src.meta.copy()
        profile.update(driver="GTiff")
        outfile = re.sub("resampled", "converted", path)
        outfile = re.sub(".jp2", ".tiff", outfile)
        with rasterio.open(outfile, 'w', **profile) as dst:
            dst.write(src.read())

def perform_jp2_to_tiff_conversion(input_dir):
    parent_dirs = get_parent_directories(input_dir)
    for parent_dir in parent_dirs:
        resampled_dir = f"{parent_dir}/resampled"
        print(f"resampled_dir : {resampled_dir}")
        converted_dir = f"{parent_dir}/converted"
        print(f"converted_dir : {converted_dir}")
        os.makedirs(converted_dir, exist_ok=True)
        jp2_images = glob.glob(f"{resampled_dir}/*_10m.jp2")
        print(f"jp2_images : {jp2_images}")
        for jp2_image in jp2_images:
            convert_jp2_to_tiff(jp2_image)

# if __name__ == "__main__":
#     today_string = date.today().strftime("%Y-%m-%d")
#     collection_name = "SENTINEL-2"  # Sentinel satellite
#     download_dir = f"data/{collection_name}/{today_string}"
#     perform_jp2_to_tiff_conversion(download_dir)


if __name__ == "__main__":
    today_string = date.today().strftime("%Y-%m-%d")
    collection_name = "SENTINEL-2"  # Sentinel satellite
    download_dir = f"data/{collection_name}/{today_string}"
    merged_band_dir = f"data/{collection_name}/{today_string}/merged"
    parent_dirs = get_parent_directories(download_dir)
    band_list = ['AOT', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12', 'SCL',
                 'TCI', 'WVP']
    resolution = 10  # Define the target resolution (e.g., 10 meters)
    for band in band_list:
        tiff_path_list = []
        for parent_dir in parent_dirs:
            print(f"parent_dir : {parent_dir}")
            tiff_path = f"{parent_dir}/converted/{band}_{resolution}m.tiff"
            if os.path.isfile(tiff_path):
                tiff_path_list.append(tiff_path)
        print(f"Band {band}m tiff files : {tiff_path_list}")
        merged_dir = f"{download_dir}/merged"
        os.makedirs(merged_dir, exist_ok=True)
        merge(tiff_path_list, f"{merged_dir}/{band}_{resolution}m.tiff", True)


