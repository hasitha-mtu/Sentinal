from datetime import date, timedelta
import requests
import pandas as pd
import geopandas as gpd
import os
from sentinelsat import read_geojson
from shapely.geometry import shape
import multiprocessing
import glob
import zipfile

copernicus_user = "adikari.adikari@mycit.ie"  # copernicus User
copernicus_password = "Hasitha@4805"  # copernicus Password
valid_http_response_codes = (301, 302, 303, 307)


def get_polygon(path):
    geojson = read_geojson(path)
    polygon_jsons = geojson["features"]
    polygon_json = polygon_jsons[0]
    geometry_data = polygon_json["geometry"]
    polygon = shape(geometry_data)
    return polygon


def get_keycloak(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]


def download_data(download_location, area_foot_print, start_date, end_date,
                  data_collection = "SENTINEL-2"):
    print(
        f"Download data from data_collection: {data_collection} from  {start_date} to {end_date} "
        f"for the area {area_foot_print}")
    products_json = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{area_foot_print}') "
        f"and ContentDate/Start gt {start_date}T00:00:00.000Z "
        f"and ContentDate/Start lt {end_date}T00:00:00.000Z&$count=True&$top=1000").json()

    # products_json = requests.get(
    #     f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' "
    #     f"and OData.CSC.Intersects(area=geography'SRID=4326;{area_foot_print}') "
    #     f"and ContentDate/Start gt {start_date}T00:00:00.000Z "
    #     f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value eq '0.3') "
    #     f"and ContentDate/Start lt {end_date}T00:00:00.000Z&$count=True&$top=1000").json()

    product_df = pd.DataFrame.from_dict(products_json['value'])
    print(f"products_df : {product_df.shape}")
    if product_df.shape[0] > 0:
        print(f"product_df info : {product_df.info()}")
        product_df["geometry"] = product_df["GeoFootprint"].apply(shape)
        geo_df = gpd.GeoDataFrame(product_df).set_geometry("geometry")  # Convert PD to GPD
        print(f"geo_df : {geo_df}")
        geo_df = geo_df[~geo_df["Name"].str.contains("L1C")]  # Remove L1 data from dataframe
        geo_df["identifier"] = geo_df["Name"].str.split(".").str[0]
        feature_count = len(geo_df)
        print(f"Total feature count in product_df : {feature_count}")
        if feature_count > 0:
            try:
                os.makedirs(download_location, exist_ok=True)
                for i, feature in enumerate(geo_df.iterfeatures()):
                    with multiprocessing.Pool() as pool:
                        pool.map(download_image_zip, [(feature, download_location)])
            except Exception as e:
                print(f"Problem with server error: {e}")
        else:
            print(f"Features not found|{feature_count}")
    else:
        print(f"No data found for the given criteria")


def download_image_zip(file_info):
    print(f"download_image_zip|file_info : {file_info}")
    feature, dir_path = file_info
    try:
        session = requests.Session()
        keycloak_token = get_keycloak(copernicus_user, copernicus_password)
        session.headers.update({"Authorization": f"Bearer {keycloak_token}"})
        url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({feature['properties']['Id']})/$value"
        response = session.get(url, allow_redirects=False)
        print(f"response : {response}")
        while response.status_code in valid_http_response_codes:
            url = response.headers["Location"]
            response = session.get(url, allow_redirects=False)
        print(feature["properties"]["Id"])
        file = session.get(url, verify=False, allow_redirects=True)
        with open(f"{dir_path}/{feature['properties']['identifier']}.zip", "wb", ) as p:
            print(feature["properties"]["Name"])
            p.write(file.content)
    except Exception as e:
        print(f"Problem with server error: {e}")

def unzip_downloaded_files(zip_dir):
    for zip_file_path in glob.glob(f"{zip_dir}/*.zip"):
        print(f"Unzipping file : {zip_file_path}")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(zip_dir)
        os.remove(zip_file_path) # Remove original zip file after extraction

if __name__ == "__main__":
    today = date.today()
    today_string = today.strftime("%Y-%m-%d")
    yesterday = today - timedelta(days=10)
    yesterday_string = yesterday.strftime("%Y-%m-%d")
    selected_area = get_polygon('config/Kenmare-map.geojson')
    collection_name = "SENTINEL-2"  # Sentinel satellite
    download_dir = f"data/{collection_name}/{today_string}"
    print(f"download_dir : {download_dir}")
    download_data(download_dir, selected_area, yesterday_string,
                  today_string, data_collection=collection_name)
    unzip_downloaded_files(download_dir)

# if __name__ == "__main__":
#     collection_name = "SENTINEL-2"  # Sentinel satellite
#     today_string = date.today().strftime("%Y-%m-%d")
#     download_dir = f"data/{collection_name}/{today_string}/raw"
#     print(f"download_dir : {download_dir}")
#     unzip_downloaded_files(download_dir)
