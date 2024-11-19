import rasterio
import numpy as np

# Define a function to apply the formula
def process_pixel(B02, B03, B04, B08, B8A, B11, B12):
    # First output
    output1 = abs(0.4809 * ((((B02 * 2.5) - 0.3329) * -9.4425) +
                            (((B03 * 2.5) - 0.3182) * 2.1846) +
                            (((B04 * 2.5) - 0.3380) * 2.5333) +
                            (((B11 * 2.5) - 0.5644) * 9.9256) +
                            (((B12 * 2.5) - 0.4216) * -13.6911)) - 0.4766)

    # Second output
    output2 = abs(0.3275 * ((((B02 * 2.5) - 0.2844) * 13.3644) +
                            (((B03 * 2.5) - 0.2736) * -6.6588) +
                            (((B04 * 2.5) - 0.2750) * -1.1994) +
                            (((B08 * 2.5) - 0.5972) * -0.2090) +
                            (((B8A * 2.5) - 0.6648) * 5.1630) +
                            (((B11 * 2.5) - 0.5651) * -7.2183)) + 0.0463)

    # Third output
    output3 = abs(0.2361 * ((((B03 * 2.5) - 0.2429) * 21.8759) +
                            (((B04 * 2.5) - 0.2321) * -6.0679) +
                            (((B08 * 2.5) - 0.4371) * -3.0608) +
                            (((B11 * 2.5) - 0.4146) * -4.4420)) + 0.2061)

    return output1, output2, output3

# Load Sentinel-2 bands
bands = {}
for band_name in ['B02', 'B03', 'B04', 'B8A', 'B11', 'B12']:
    with rasterio.open(f'config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_{band_name}_20m.jp2') as src:
        bands[band_name] = src.read(1)

for band_name in ['B08']:
    with rasterio.open(f'config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R10m/T29UMT_20241118T115359_{band_name}_10m.jp2') as src:
        bands[band_name] = src.read(1)

print(f"bands : {bands}")
# Process the image
outputs = [np.zeros_like(bands['B02']) for _ in range(3)]
print(f"outputs : {outputs}")

for i in range(bands['B02'].shape[0]):
    for j in range(bands['B02'].shape[1]):
        B02, B03, B04, B08, B8A, B11, B12 = (
            bands['B02'][i, j], bands['B03'][i, j], bands['B04'][i, j],
            bands['B08'][i, j], bands['B8A'][i, j], bands['B11'][i, j],
            bands['B12'][i, j]
        )
        outputs[0][i, j], outputs[1][i, j], outputs[2][i, j] = process_pixel(B02, B03, B04, B08, B8A, B11, B12)

print(f"outputs : {outputs}")
# Save outputs as GeoTIFF
file_list = []
for idx, output in enumerate(outputs):
    tiff_file = f'data/output/output_{idx+1}.tif'
    with rasterio.open(
        tiff_file, 'w',
        driver='GTiff',
        height=output.shape[0],
        width=output.shape[1],
        count=1,
        dtype=output.dtype,
        crs=src.crs,
        transform=src.transform
    ) as dst:
        dst.write(output, 1)
        file_list.append(tiff_file)
print(f"file_list : {file_list}")
# gg = gdal.BuildVRT("", file_list, separate=True)
# g = gdal.Translate("output.tif", gg, fmt="GTiff")