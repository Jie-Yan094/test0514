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

###############################################
# 以下是網頁內容
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")

# 地理區域（彰化師大附近）
my_point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 取得 Sentinel-2 影像
my_image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(my_point) \
    .filterDate('2021-01-01', '2022-01-01') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')

vis_params = {
    'min': 100,
    'max': 3500,
    'bands': ['B11', 'B8', 'B3']
}

# 建立訓練資料
training001 = my_image.sample(
    region=my_image.geometry(),
    scale=10,
    numPixels=10000,
    seed=0,
    geometries=True,
)

# 使用 wekaKMeans 群集器（可指定群數）
clusterer_KMeans = ee.Clusterer.wekaKMeans(numClusters=10).train(training001)
result001 = my_image.cluster(clusterer_KMeans)

# 建立顏色圖例（剛好 10 群）
legend_dict1 = {
    '0': '#1c5f2c',
    '1': '#ab0000',
    '2': '#d99282',
    '3': '#ff0004',
    '4': '#ab6c28',
    '5': '#466b9f',
    '6': '#10d22c',
    '7': '#fae6a0',
    '8': '#f0f0f0',
    '9': '#58481f',
}
palette = list(legend_dict1.values())
vis_params_001 = {'min': 0, 'max': 9, 'palette': palette}

# 顯示地圖
left_layer = geemap.ee_tile_layer(result001, vis_params_001, "KMeans clustered land cover")
right_layer = geemap.ee_tile_layer(my_image, vis_params, "Sentinel-2")

my_Map = geemap.Map(center=[24.081653403304525, 120.5583462887228], zoom=9)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='KMeans_Land Cover Type', legend_dict=legend_dict1, draggable=False, position='bottomleft')
my_Map.to_streamlit(height=600)
