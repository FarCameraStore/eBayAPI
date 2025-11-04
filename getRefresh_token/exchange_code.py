# -*- coding: utf-8 -*-

import requests
import base64
import json
import sys

# ==============================================================================
# --- 1. 请在这里填入您的信息 ---
# ==============================================================================

# 您的应用凭证，从 eBay 开发者后台 (developer.ebay.com) 获取
APP_ID = ""
CERT_ID = ""

# 之前通过 ngrok 生成并配置到 eBay 后台的 Redirect URI (RuName)
# 必须和 eBay 后台设置的完全一致！
REDIRECT_URI = "https://1234567890.ngrok-free.app/"

# 运行 capture_code.py 后，从终端捕获到的一次性授权码
AUTH_CODE = ""

# ==============================================================================
# --- 2. 脚本将使用以上信息执行操作 (通常无需修改以下内容) ---
# ==============================================================================

def exchange_code_for_token():
    """
    使用授权码向 eBay 服务器交换 Refresh Token。
    """
    # 检查用户是否已填写信息
    if "YOUR_" in APP_ID or "PASTE_" in AUTH_CODE or "YOUR_" in REDIRECT_URI:
        print("错误：请先编辑此脚本文件，")
        print("将顶部的占位符（例如 'YOUR_APP_ID_HERE'）替换为您的真实信息。")
        sys.exit(1)

    # eBay OAuth 2.0 Token 端点
    token_url = 'https://api.ebay.com/identity/v1/oauth2/token'

    # 准备请求头 (Basic Authentication)
    # 格式为 base64(app_id:cert_id)
    credentials = f"{APP_ID}:{CERT_ID}"
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64_credentials}'
    }

    # 准备请求体
    body = {
        'grant_type': 'authorization_code',
        'code': AUTH_CODE,
        'redirect_uri': REDIRECT_URI
    }

    try:
        print("正在向 eBay 服务器发送请求，请稍候...")
        response = requests.post(token_url, headers=headers, data=body)

        # 检查请求是否成功
        if response.status_code == 200:
            token_data = response.json()
            print("\n" + "="*80)
            print("🎉 成功！已成功用授权码换取到 Token 信息。")
            print("="*80)
            # 使用 json.dumps 美化输出，确保中文等字符正常显示
            print(json.dumps(token_data, indent=4, ensure_ascii=False))
            print("\n" + "="*80)
            print("下一步操作：")
            print("1. 从上面的 JSON 结果中复制 'refresh_token' 的值 (这是一长串字符)。")
            print("2. 从上面的 JSON 结果中复制 'refresh_token_expiry' 的值 (这是一个数字)。")
            print("3. 将这两个值手动粘贴到您的 `ebay_rest.json` 文件中对应的位置。")
            print("="*80)
        else:
            print(f"\n错误：请求失败，HTTP 状态码: {response.status_code}")
            print("服务器返回的错误信息:")
            # 尝试以JSON格式解析错误信息，如果失败则直接打印文本
            try:
                print(json.dumps(response.json(), indent=4))
            except json.JSONDecodeError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"\n网络请求时发生严重错误: {e}")
        print("请检查您的网络连接，以及 APP_ID 等信息是否正确。")


if __name__ == "__main__":
    exchange_code_for_token()