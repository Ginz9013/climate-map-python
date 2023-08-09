import http.server
import socketserver
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import json


PORT = 8080

# 使用 geopandas 載入 GeoJSON 資料
gdf = gpd.read_file("taiwan.json")

# 建立地圖
fig, ax = plt.subplots()
gdf.plot(ax=ax)
# 關閉座標軸
ax.axis('off')


# ---- 取得氣溫資料 ----
response = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-0AFFC5D1-340B-437D-8E6E-BFEACCCBB52B')

if response.status_code == 200:
    # 解析 API 响应并发送
    data = response.json()
    
    if 'records' in data:

        tempList = {}
        dtxList = {}
        dtnList = {}

        # 取得溫度資料並寫入 gdf 中
        for station in data['records']['location']:
            key = station['parameter'][0]['parameterValue']
            temp = station['weatherElement'][3]['elementValue']
            dtx = station['weatherElement'][10]['elementValue']
            dtn = station['weatherElement'][12]['elementValue']

            # 先確認均溫為正常數字
            if temp != '-99':
                # 如果 tempList 中沒有該縣市的資料
                if key not in tempList:
                    tempList[key] = temp
                else:
                    tempList[key] = round((float(tempList[key]) + float(temp)) / 2, 2)

            # 先確認最高溫為正常數字
            if dtx != '-99':
                # 如果 dtxList 中沒有該縣市的資料
                if key not in dtxList:
                    dtxList[key] = dtx
                else:
                    dtxList[key] = round((float(dtxList[key]) + float(dtx)) / 2, 2)

            if dtn != '-99':
                # 如果 dtnList 中沒有該縣市的資料
                if key not in dtnList:
                    dtnList[key] = dtn
                else:
                    dtnList[key] = round((float(dtnList[key]) + float(dtn)) / 2, 2)

        gdf['temp'] = gdf.NAME_2014.map(tempList)
        gdf['D_TX'] = gdf.NAME_2014.map(dtxList)
        gdf['D_TN'] = gdf.NAME_2014.map(dtnList)
else:
    error_message = {'error': 'Failed to fetch data from external API'}
    print(error_message)
# ---- 取得氣溫資料 ----



# ---- 取得紫外線資料 ----
# 取得觀測站資料（靜態）
# 讀取本地 JSON 檔案
with open('stations.json', 'r') as file:
    stationData = json.load(file)

# 站點資料
# stationList = stationData.cwbdata.resources.resource.data.stationsStatus.station
stationList = stationData['cwbdata']['resources']['resource']['data']['stationsStatus']['station']

# 紫外線資料
res = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0005-001?Authorization=CWB-0AFFC5D1-340B-437D-8E6E-BFEACCCBB52B')

if res.status_code == 200:
    uviResData = res.json()

    if 'records' in uviResData:
        
        uviList = uviResData['records']['weatherElement']['location']

        uviData = {}

        for location in uviList:
            for station in stationList:
                if location['locationCode'] == station['StationID']:
                    county = station['CountyName']
                    if county not in uviData:
                        uviData[county] = location['value']
                    else:
                        uviData[county] = round((float(uviData[county]) + float(location['value'])) / 2, 2)

        gdf['uvi'] = gdf.NAME_2014.map(uviData)
else:
    error_message = {'error': 'Failed to fetch data from external API'}
# ---- 取得紫外線資料 ----


# ---- 取得降雨資料 ----
rainfallRes = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=CWB-0AFFC5D1-340B-437D-8E6E-BFEACCCBB52B&limit=100&parameterName=CITY')

if rainfallRes.status_code == 200:
    rainfallResData = rainfallRes.json()

    if 'records' in rainfallResData:
        rainfallInfo = rainfallResData['records']['location']
# ---- 取得降雨資料 ----

# ---- 取得站點資料 ----
stationRes = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-0AFFC5D1-340B-437D-8E6E-BFEACCCBB52B')

if stationRes.status_code == 200:
    stationData = stationRes.json()

    if 'records' in rainfallResData:
        stations = stationData['records']['location']

# ---- 取得站點資料 ----

# 建立 http 
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # 傳送 index.html 至前端 
            with open("public/index.html", "rb") as html_file:
                html_content = html_file.read()
            self.wfile.write(html_content)

            return
        elif self.path == '/taiwan.geojson':
            self.send_response(200)
            self.send_header('Content-type', 'application/geo+json')
            self.end_headers()

            # 將 gdf(geoDataFrame) 資料轉成字串後用 UTF-8 編碼傳送
            self.wfile.write(gdf.to_json().encode('utf-8'))
            return
        elif self.path == '/rainfall.info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # 將 rainfallInfo 資料轉成字串後用 UTF-8 編碼傳送
            self.wfile.write(json.dumps(rainfallInfo).encode('utf-8'))
            return
        elif self.path == '/stations.info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # 將 rainfallInfo 資料轉成字串後用 UTF-8 編碼傳送
            self.wfile.write(json.dumps(stations).encode('utf-8'))
            return

# 使用 SimpleHTTPRequestHandler 創建伺服器
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), MyHandler)

print(f"Serving at port {PORT}")
httpd.serve_forever()