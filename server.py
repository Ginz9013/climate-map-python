import http.server
import socketserver
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO

PORT = 8000

# 使用 geopandas 加载 GeoJSON 数据
gdf = gpd.read_file("taiwan.json")

# 创建地图图表
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='blue', edgecolor='black')

# 保存图表到 BytesIO 对象
buffer = BytesIO()
plt.savefig(buffer, format='png')
plt.close()

# 创建 HTTP 服务器处理程序
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # 在响应中嵌入图像的显示
            self.wfile.write(b'<html><body>')
            self.wfile.write(b'<h1>GeoPandas Plot</h1>')
            self.wfile.write(b'<img src="/plot.png" alt="GeoPandas Plot">')
            self.wfile.write(b'</body></html>')
            return
        elif self.path == '/plot.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            # 发送图像数据
            buffer.seek(0)
            self.wfile.write(buffer.read())
            return

# 启动 HTTP 服务器
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()