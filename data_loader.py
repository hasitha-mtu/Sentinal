from sentinelsat import SentinelAPI

# Connect to Copernicus Open Access Hub
api = SentinelAPI('username', 'password', 'https://scihub.copernicus.eu/dhus')

# Query for Sentinel-2 data
products = api.query(area_of_interest_geojson,
                     date=('20240101', '20240131'),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 20))

# Download data
api.download_all(products, directory_path='/path/to/save/data')