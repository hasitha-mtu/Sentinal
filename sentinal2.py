from datetime import date, timedelta
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import os

copernicus_user = "adikari.adikari@mycit.ie" # copernicus User
copernicus_password = "Hasitha@4805" # copernicus Password
# ft = "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"  # WKT Representation of BBOX
ft = "POLYGON((-11.365176174401597 55.61826819268245, -11.365176174401597 51.36812029144471, -5.371103152042821 51.36812029144471, -5.371103152042821 55.61826819268245, -11.365176174401597 55.61826819268245))"  # WKT Representation of BBOX
data_collection = "SENTINEL-2" # Sentinel satellite

today =  date.today() - timedelta(days=1)
today_string = today.strftime("%Y-%m-%d")
yesterday = today - timedelta(days=2)
yesterday_string = yesterday.strftime("%Y-%m-%d")

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

if __name__ == "__main__":
    json_ = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{ft}') and ContentDate/Start gt {yesterday_string}T00:00:00.000Z "
        f"and ContentDate/Start lt {today_string}T00:00:00.000Z&$count=True&$top=1000").json()
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

                    with open(
                            f"{feat['properties']['identifier']}.zip",  # location to save zip from copernicus
                            "wb",
                    ) as p:
                        print(feat["properties"]["Name"])
                        p.write(file.content)
                except:
                    print("problem with server")
    else:
        print('no data found')

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
if __name__ == "__main__":
    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson('config/map.geojson'))
    print(f"footprint: {footprint}")



