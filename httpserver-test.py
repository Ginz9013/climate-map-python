import http.server
import socketserver

# 定義 port
PORT = 8080

# 切换到要共享的目录
DIRECTORY = "."  # 当前目录

# 创建一个简单的 HTTP 请求处理程序
Handler = http.server.SimpleHTTPRequestHandler

# 创建一个服务器实例，监听指定的端口
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port", PORT)
    # 开始监听请求，直到用户终止服务器
    httpd.serve_forever()