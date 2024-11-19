import rasterio
import matplotlib.pyplot as plt


with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B02_20m.jp2') as b02_band:
    B02 = b02_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B03_20m.jp2') as b03_band:
    B03 = b03_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B04_20m.jp2') as b04_band:
    B04 = b04_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R10m/T29UMT_20241118T115359_B08_10m.jp2') as b08_band:
    B08 = b08_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B8A_20m.jp2') as b08a_band:
    B8A = b08a_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B11_20m.jp2') as b11_band:
    B11 = b11_band.read(1)
with rasterio.open('config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE/GRANULE/L2A_T29UMT_A040232_20241118T115357/IMG_DATA/R20m/T29UMT_20241118T115359_B12_20m.jp2') as b12_band:
    B12 = b12_band.read(1)

def create_tif():
    # Compute Custom
    # custom = [abs(0.4809 * ((((B02 * 2.5) - 0.3329) * -9.4425) + (((B03 * 2.5) - 0.3182) * 2.1846) + (
    #             ((B04 * 2.5) - 0.3380) * 2.5333) + (((B11 * 2.5) - 0.5644) * 9.9256) + (
    #                                     ((B12 * 2.5) - 0.4216) * -13.6911)) + -0.4766),
    #           abs(0.3275 * ((((B02 * 2.5) - 0.2844) * 13.3644) + (((B03 * 2.5) - 0.2736) * -6.6588) + (
    #                       ((B04 * 2.5) - 0.2750) * -1.1994) + (((B08 * 2.5) - 0.5972) * -0.2090) + (
    #                                     ((B8A * 2.5) - 0.6648) * 5.1630) + (
    #                                     ((B11 * 2.5) - 0.5651) * -7.2183)) + 0.0463),
    #           abs(0.2361 * ((((B03 * 2.5) - 0.2429) * 21.8759) + (((B04 * 2.5) - 0.2321) * -6.0679) + (
    #                       ((B08 * 2.5) - 0.4371) * -3.0608) + (((B11 * 2.5) - 0.4146) * -4.4420)) + 0.2061)]

    custom = [abs(0.4809 * ((((B02 * 2.5) - 0.3329) * -9.4425) + (((B03 * 2.5) - 0.3182) * 2.1846) + (
                ((B04 * 2.5) - 0.3380) * 2.5333) + (((B11 * 2.5) - 0.5644) * 9.9256) + (
                                        ((B12 * 2.5) - 0.4216) * -13.6911)) + -0.4766),
              abs(0.3275 * ((((B02 * 2.5) - 0.2844) * 13.3644) + (((B03 * 2.5) - 0.2736) * -6.6588) + (
                          ((B04 * 2.5) - 0.2750) * -1.1994) + (((B8A * 2.5) - 0.5972) * -0.2090) + (
                                        ((B8A * 2.5) - 0.6648) * 5.1630) + (
                                        ((B11 * 2.5) - 0.5651) * -7.2183)) + 0.0463),
              abs(0.2361 * ((((B03 * 2.5) - 0.2429) * 21.8759) + (((B04 * 2.5) - 0.2321) * -6.0679) + (
                          ((B8A * 2.5) - 0.4371) * -3.0608) + (((B11 * 2.5) - 0.4146) * -4.4420)) + 0.2061)]

    # Plot Custom
    plt.imshow(custom, cmap='RdYlGn')
    plt.colorbar(label='Custom')
    plt.title('Custom Map')
    plt.show()

    # Save NDVI as GeoTIFF
    with rasterio.open(
            'config/custom.tif',
            'w',
            driver='GTiff',
            height=custom.shape[0],
            width=custom.shape[1],
            count=1,
            dtype=custom.dtype
            # crs=nir_band.crs,
            # transform=nir_band.transform,
    ) as dst:
        dst.write(custom, 1)

if __name__ == "__main__":
    create_tif()

