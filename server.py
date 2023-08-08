import http.server
import socketserver
import geopandas as gpd
import matplotlib.pyplot as plt
from io import StringIO
import requests
import json


PORT = 8088

# 使用 geopandas 載入 GeoJSON 資料
gdf = gpd.read_file("taiwan.json")

# 建立地圖
fig, ax = plt.subplots()
gdf.plot(ax=ax)
# 關閉座標軸
ax.axis('off')

tempDataList = {};

# ---- 取得氣候資料 ----
response = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-0AFFC5D1-340B-437D-8E6E-BFEACCCBB52B')

if response.status_code == 200:
    # 解析 API 响应并发送
    data = response.json()
    
    if 'records' in data:
        # climate_data = {
        #     record['CITY']: record['climate_value'] for record in data['records']['location']
        # }
        for station in data['records']['location']:
            tempDataList[station['parameter'][0]['parameterValue']] = station['weatherElement'][3]['elementValue']
        print(tempDataList)
        gdf['temp'] = gdf.NAME_2014.map(tempDataList)
        print(gdf.temp)

        # 使用 matplotlib 套件中提供的漸層顏色
        cmap = plt.cm.get_cmap('viridis')

        # 透過資料給地圖上色
        gdf.plot(column='temp', cmap=cmap, linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
else:
    error_message = {'error': 'Failed to fetch data from external API'}
    print(error_message)
# ---- 取得氣候資料 ----

# 將資料保存成 SVG 字串
buffer = StringIO()
plt.savefig(buffer, format='svg', bbox_inches='tight')
svg_data = buffer.getvalue()
buffer.close()

plt.close()


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
        elif self.path == '/plot.svg':  # 新增 SVG 路徑
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')  # 設置 Content-type 為 SVG 格式
            self.end_headers()

            # 直接將 SVG 字串寫入伺服器輸出流
            self.wfile.write(svg_data.encode('utf-8'))
            return

# 使用 SimpleHTTPRequestHandler 創建伺服器
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), MyHandler)

print(f"Serving at port {PORT}")
httpd.serve_forever()