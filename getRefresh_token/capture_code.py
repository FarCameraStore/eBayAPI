#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本脚本启动一个本地HTTP服务器，专门用于捕获 eBay OAuth 2.0 授权流程
成功后从回调 URL (Redirect URI) 中传递过来的一次性授权码 (Authorization Code)。
"""

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import sys

# 服务器监听的端口，必须与 ngrok 转发的端口一致
PORT = 8000

class CodeCaptureHandler(http.server.BaseHTTPRequestHandler):
    """
    一个自定义的请求处理器，用于解析GET请求并提取'code'参数。
    """
    def do_GET(self):
        """处理传入的GET请求"""
        print(f"\n收到来自 {self.client_address[0]} 的请求: {self.path}")

        # 解析请求的URL路径和查询参数
        parsed_path = urlparse(self.path)
        query_components = parse_qs(parsed_path.query)

        # 检查URL中是否包含 'code' 参数
        if 'code' in query_components:
            # 提取授权码 (通常只有一个)
            auth_code = query_components["code"][0]

            # 在终端中用非常显眼的方式打印出捕获到的授权码
            print("\n" + "="*80)
            print("🎉 成功捕获到授权码 (Authorization Code)！")
            print("\n授权码是:")
            print(f"    {auth_code}")
            print("\n" + "="*80)
            print("\n下一步操作：")
            print("1. 请完整复制上面的授权码。")
            print(f"2. 将它粘贴到 `exchange_code.py` 脚本的 `AUTH_CODE` 变量中。")
            print("3. 运行 `exchange_code.py` 脚本来换取最终的 Refresh Token。")
            print("\n这个服务器的任务已完成，您可以按 Ctrl+C 来关闭它。")

            # 向浏览器返回一个成功的HTML页面，提供更好的用户体验
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            response_html = """
            <html>
            <head><title>授权成功</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>✅ 授权码已成功捕获！</h1>
                <p>您现在可以关闭这个浏览器标签页，并返回到您的终端窗口查看已捕获的授权码。</p>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode('utf-8'))

        else:
            # 如果请求中没有 'code'，则显示一个等待页面
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            wait_html = """
            <html>
            <body style="font-family: sans-serif;">
                <p>服务器正在运行，等待来自 eBay 的授权跳转...</p>
            </body>
            </html>
            """
            self.wfile.write(wait_html.encode('utf-8'))

def run_server():
    """启动服务器"""
    try:
        # 使用 with 语句确保服务器资源被正确管理
        with socketserver.TCPServer(("", PORT), CodeCaptureHandler) as httpd:
            print("="*50)
            print(f"本地授权码捕获服务器已在 http://localhost:{PORT} 启动")
            print("请确保您的 ngrok 正在将一个 https 地址转发到此端口。")
            print("现在，请去触发 eBay 的浏览器授权流程。")
            print("服务器正在等待 eBay 的回调...")
            print("="*50)
            # 持续运行服务器，直到手动停止
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，服务器已关闭。")
        sys.exit(0)
    except OSError as e:
        print(f"\n错误：无法启动服务器，端口 {PORT} 可能已被占用。")
        print(f"详细信息: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()