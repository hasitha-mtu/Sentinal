from datetime import date
from data_re_projection import perform_re_projection
from data_resampling import resample_images


def perform_data_preprocessing(file_path):
    resolution_list = [10, 20, 60]
    band_list = ['AOT', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12', 'SCL',
                 'TCI', 'WVP']
    resample_images(10, file_path, resolution_list=resolution_list, band_list=band_list)
    # perform_re_projection(file_path)

if __name__ == "__main__":
    collection_name = "SENTINEL-2"
    resolution = 10 # Define the target resolution (e.g., 10 meters)
    today_string = date.today().strftime("%Y-%m-%d")
    download_dir = f"data/{collection_name}/{today_string}"
    print(f"download_dir : {download_dir}")
    perform_data_preprocessing(download_dir)



