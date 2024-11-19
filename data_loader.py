from sentinelsat import SentinelAPI

def download_data(area_of_interest_geojson):
    # Connect to Copernicus Open Access Hub
    api = SentinelAPI('adikari.adikari@mycit.ie', 'Hasitha@4805', 'https://dataspace.copernicus.eu/')

    # Query for Sentinel-2 data
    products = api.query(area_of_interest_geojson,
                         date=('20240101', '20240131'),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 20))

    # Download data
    api.download_all(products, directory_path='/path/to/save/data')

if __name__ == "__main__":
    download_data('config/map.geojson')