import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON (解讀)
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)

#以上皆為不能改的內容
###############################################
#以下是網頁內容
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")


# 地理區域
my_point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

my_image =ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(my_point) \
    .filterDate('2021-01-01', '2022-01-01') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
sentinel_nd = my_image.normalizedDifference(["B11", "B8", "B3"]).rename("Sentinel_ND")

training001 = my_image.sample(
    region=my_image.geometry(),
    scale=10,
    numPixels=10000,
    seed=0,
    geometries=True,
)

# 訓練群集器，指定為 10 群
clusterer_CascadeKMeans = ee.Clusterer.wekaCascadeKMeans(numClusters=10).train(training001)
result001 = my_image.cluster(clusterer_CascadeKMeans)

# Legend palette
legend_dict1 = {
    'zero': '#1c5f2c',
    'one': '#ab0000',
    'two': '#d99282',
    'three': '#ff0004',
    'four': '#ab6c28',
    'five': '#466b9f',
    'six': '#10d22c',
    'seven': '#fae6a0',
    'eight': '#f0f0f0',
    'nine': '#58481f',
    'ten': '#a0dc00',
}
palette = list(legend_dict1.values())
vis_params_001 = {'min': 0, 'max': 9, 'palette': palette}

# 地圖顯示
left_layer = geemap.ee_tile_layer(result001, vis_params_001, "wekaCascadeKMeans clustered land cover")
right_layer = geemap.ee_tile_layer(my_image, vis_params, "Sentinel-2")

my_Map = geemap.Map(center=[24.081653403304525, 120.5583462887228], zoom=9)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='CascadeKMeans_Land Cover Type', legend_dict=legend_dict1, draggable=False, position='bottomleft')
my_Map.to_streamlit(height=600)
