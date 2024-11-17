from datetime import date, timedelta
import requests
import pandas as pd
import geopandas as gpd
import os
from sentinelsat import read_geojson
from shapely.geometry import shape

copernicus_user = "adikari.adikari@mycit.ie" # copernicus User
copernicus_password = "Hasitha@4805" # copernicus Password
data_collection = "SENTINEL-2" # Sentinel satellite


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

def download_data(start_date, end_date):
    ft = get_polygon('config/map.geojson')
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
    download_data(yesterday_string, today_string)



