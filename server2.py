import http.server
import socketserver
import geopandas as gpd

PORT = 8080

# 加载 GeoJSON 数据
gdf = gpd.read_file("taiwan.json")

# 将数据转换为 SVG 格式
svg_data = gdf.to_svg()

# 创建 HTTP 服务器处理程序
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # 在响应中嵌入 SVG 的显示
            self.wfile.write(b'<html><body>')
            self.wfile.write(b'<h1>GeoPandas SVG</h1>')
            self.wfile.write(b'<div>')
            self.wfile.write(svg_data.encode())
            self.wfile.write(b'</div>')
            self.wfile.write(b'</body></html>')
            return

# 启动 HTTP 服务器
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()