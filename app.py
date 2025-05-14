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


training001 = my_image.sample(
    **{
        'region': my_image.geometry(),  # 若不指定，則預設為影像my_image的幾何範圍。
        'scale': 10,
        'numPixels': 10000,
        'seed': 0, #亂數種子(亂數產生的出發點，可用作檢核過程)
        'geometries': True,  # 設為False表示取樣輸出的點將忽略其幾何屬性(即所屬網格的中心點)，無法作為圖層顯示，可節省記憶體。
    }
)
clusterer_CascadeKMeans = ee.Clusterer.wekaCascadeKMeans().train(training001)
result001 = my_image.cluster(clusterer_CascadeKMeans)
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
    'night': '#58481f',
    'ten': '#a0dc00',
}
# 為分好的每一群賦予標籤

palette = list(legend_dict1.values())
vis_params_001 = {'min': 0, 'max': 11, 'palette': palette}

# 顯示地圖


left_layer = geemap.ee_tile_layer(result001, vis_params_001, "wekaCascadeKMeans clustered land cover")
right_layer = geemap.ee_tile_layer(my_image, vis_params, "Sentinel-2")

my_Map = geemap.Map(center=[120.5583462887228, 24.081653403304525], zoom=9)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='CascadeKMeans_Land Cover Type', legend_dict = legend_dict1, draggable=False, position = 'bottomleft')
my_Map.to_streamlit(height=600) #把圖畫出來(height=圖的高)
