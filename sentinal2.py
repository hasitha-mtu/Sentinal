from datetime import date, timedelta
import requests
import pandas as pd
import geopandas as gpd
import os
from sentinelsat import read_geojson
from shapely.geometry import shape
import multiprocessing

copernicus_user = "adikari.adikari@mycit.ie" # copernicus User
copernicus_password = "Hasitha@4805" # copernicus Password


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

def download_data(data_collection, area_foot_print, start_date, end_date):
    print(f"Download data from data_collection: {data_collection} from  {start_date} to {end_date} for the area {area_foot_print}")
    products_json = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{area_foot_print}') and ContentDate/Start gt {start_date}T00:00:00.000Z "
        f"and ContentDate/Start lt {end_date}T00:00:00.000Z&$count=True&$top=1000").json()

    product_df = pd.DataFrame.from_dict(products_json['value'])
    print(f"products_df : {product_df.shape}")
    if product_df.shape[0]>0:
        print(f"product_df info : {product_df.info()}")
        product_df["geometry"] = product_df["GeoFootprint"].apply(shape)
        geo_df = gpd.GeoDataFrame(product_df).set_geometry("geometry")  # Convert PD to GPD
        print(f"geo_df : {geo_df}")
        geo_df = geo_df[~geo_df["Name"].str.contains("L1C")]
        geo_df["identifier"] = geo_df["Name"].str.split(".").str[0]
        feature_count = len(geo_df)
        if feature_count > 0:
            try:
                dir_path = f"data/{data_collection}/{today_string}"
                os.makedirs(dir_path, exist_ok=True)
                for i, feature in enumerate(geo_df.iterfeatures()):
                    with multiprocessing.Pool() as pool:
                        pool.map(download_image_zip, [(feature, dir_path)])
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
        while response.status_code in (301, 302, 303, 307):
            url = response.headers["Location"]
            response = session.get(url, allow_redirects=False)
        print(feature["properties"]["Id"])
        file = session.get(url, verify=False, allow_redirects=True)
        with open(f"{dir_path}/{feature['properties']['identifier']}.zip", "wb", ) as p:
            print(feature["properties"]["Name"])
            p.write(file.content)
    except Exception as e:
        print(f"Problem with server error: {e}")

def download_data1(start_date, end_date):
    ft = get_polygon('config/map.geojson')
    # https://catalogue.dataspace.copernicus.eu/odata/v1/DeletedProducts?$filter=Collection/Name%20eq%20%27SENTINEL-1%27%20and%20DeletionDate%20gt%202023-04-01T00:00:00.000Z%20and%20DeletionDate%20lt%202023-05-30T23:59:59.999Z&$orderby=DeletionDate&$top=20
    json_ = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{ft}') and ContentDate/Start gt {start_date}T00:00:00.000Z "
        f"and ContentDate/Start lt {end_date}T00:00:00.000Z&$count=True&$top=1000").json()
    print(f"Request: {json_}")
    p = pd.DataFrame.from_dict(json_["value"])  # Fetch available dataset
    if p.shape[0] > 0:
        p["geometry"] = p["GeoFootprint"].apply(shape)
        productDF = gpd.GeoDataFrame(p).set_geometry("geometry")  # Convert PD to GPD
        productDF = productDF[~productDF["Name"].str.contains("L1C")]  # Remove L1C dataset
        print(f" total L2A tiles found {len(productDF)}")
        productDF["identifier"] = productDF["Name"].str.split(".").str[0]
        allfeat = len(productDF)

        if allfeat == 0:
            print("No tiles found for today")
        else:
            ## download all tiles from server
            for index, feat in enumerate(productDF.iterfeatures()):
                try:
                    session = requests.Session()
                    keycloak_token = get_keycloak(copernicus_user, copernicus_password)
                    session.headers.update({"Authorization": f"Bearer {keycloak_token}"})
                    url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({feat['properties']['Id']})/$value"
                    response = session.get(url, allow_redirects=False)
                    while response.status_code in (301, 302, 303, 307):
                        url = response.headers["Location"]
                        response = session.get(url, allow_redirects=False)
                    print(feat["properties"]["Id"])
                    file = session.get(url, verify=False, allow_redirects=True)
                    dir_path = f"data/{data_collection}/{today_string}"
                    os.makedirs(dir_path, exist_ok=True)
                    with open( f"{dir_path}/{feat['properties']['identifier']}.zip", "wb", ) as p:
                        print(feat["properties"]["Name"])
                        p.write(file.content)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    print("problem with server")
    else:
        print('no data found')

if __name__ == "__main__":
    today = date.today()
    today_string = today.strftime("%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    yesterday_string = yesterday.strftime("%Y-%m-%d")
    area_foot_print = get_polygon('config/map.geojson')
    data_collection = "SENTINEL-2"  # Sentinel satellite
    download_data(data_collection, area_foot_print, yesterday_string, today_string)



