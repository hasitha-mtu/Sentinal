import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from datetime import date
import os
import glob
import shutil

def perform_resampling1(input_file, output_file, target_resolution = 10):
    # Load the Sentinel-2 image
    with rasterio.open(input_file) as src:
        img = src.read()
        profile = src.profile

    # Calculate the transformation and resampling method
    transform, width, height = calculate_default_transform(
        src.crs, src.crs, src.width, src.height, target_resolution, target_resolution
    )

    # Resample the image
    resampled_img = np.zeros((img.shape[0], height, width), dtype=img.dtype)
    for i in range(img.shape[0]):
        reproject(
            source=img[i],
            destination=resampled_img[i],
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=src.crs,
            resampling=Resampling.bilinear
        )

    # Update the profile with the new dimensions and transform
    profile.update({
        'width': width,
        'height': height,
        'transform': transform
    })

    # Write the resampled image to a new file
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(resampled_img)

def perform_resampling(input_file, output_file, upscale_factor = 2):
    with rasterio.open(input_file) as dataset:
        resampled_data = dataset.read(
            out_shape=(
                dataset.count,
                int(dataset.height * upscale_factor),
                int(dataset.width * upscale_factor)
            ),
            resampling=Resampling.bilinear)
        transform_dataset = dataset.transform * dataset.transform.scale(
            (dataset.width / resampled_data.shape[-1]),
            (dataset.height / resampled_data.shape[-2])
        )
        resampled_shape = resampled_data.shape

    with rasterio.open(output_file, mode="w", driver="JPEG", width=resampled_shape[2],
                       height=resampled_shape[1], count=1, crs=dataset.crs,
                       transform=transform_dataset, dtype=resampled_data.dtype) as dst:
        dst.write(resampled_data)

def select_directory_list(directory_path, prefix, depth):
    directory_list = []
    for root, dirs, files in os.walk(directory_path):
        if root[len(directory_path):].count(os.sep) < depth:
            for dir in dirs:
                if prefix:
                    if dir.endswith(prefix):
                        directory_list.append(dir)
                else:
                    directory_list.append(dir)
    directory_list.reverse()
    return directory_list

def band_image_directories(download_dir):
    parent_list = select_directory_list(download_dir, ".SAFE", 2)
    dir_list = []
    for dir in parent_list:
        dir_path = f"{download_dir}/{dir}/GRANULE"
        parent_list1 = select_directory_list(dir_path, None, 1)
        dir_path1 = f"{dir_path}/{parent_list1[0]}/IMG_DATA"
        dir_list.append(dir_path1)
    return dir_list

def get_image_for_the_band(dir_path, resolution, band_name):
    rez_dir = f"{image_dir}/R{resolution}m"
    images = glob.glob(f"{rez_dir}/*_{band_name}_{resolution}m.jp2")
    # print(f"images : {images}")
    return images

if __name__ == "__main__":
    collection_name = "SENTINEL-2"
    resolution = 10 # Define the target resolution (e.g., 10 meters)
    today_string = date.today().strftime("%Y-%m-%d")
    download_dir = f"data/{collection_name}/{today_string}/raw"
    print(f"download_dir : {download_dir}")
    image_dir_list = band_image_directories(download_dir)
    band_list = ['AOT', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12', 'SCL', 'TCI', 'WVP']
    for image_dir in image_dir_list:
        print("---------------------------------------------------------------------------------")
        resample_dir = f"{image_dir}/resampled"
        os.makedirs(resample_dir, exist_ok=True)
        for band in band_list:
            band_images = get_image_for_the_band(image_dir, 10, band)
            if len(band_images)>0:
                shutil.copyfile(band_images[0], f"{resample_dir}/{band}_{resolution}.jp2")
                print(band_images[0])
            else:
                band_images = get_image_for_the_band(image_dir, 20, band)
                if len(band_images)>0:
                    perform_resampling(band_images[0], f"{resample_dir}/{band}_{resolution}.jp2",
                                       upscale_factor=2)
                    print(band_images[0])
                else:
                    band_images = get_image_for_the_band(image_dir, 60, band)
                    if len(band_images) > 0:
                        perform_resampling(band_images[0], f"{resample_dir}/{band}_{resolution}.jp2",
                                           upscale_factor=6)
                        print(band_images[0])



