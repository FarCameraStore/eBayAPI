# 如何为 eBay REST API 更新 Refresh Token

**文档更新于：2025年9月14日**

本文档记录了在 Refresh Token 过期后（通常为1.5年），如何为本项目的 `ebay_rest` 库重新生成一个新的长期有效 Token 的完整步骤。

### 所需脚本和文件

本项目目录下应包含执行此操作所需的全部脚本：
- `capture_code.py`: 用于启动本地服务器捕获 eBay 返回的授权码。
- `exchange_code.py`: 用于将捕获到的授权码交换为最终的 Refresh Token。
- `calculate_expiry.py`: (可选但强烈推荐) 用于将 eBay 返回的有效期秒数转换为配置文件所需的时间字符串格式。
- `ebay_rest.json`: 存储应用凭证和最终获取到的 Token 的配置文件。

**核心流程**：由于 `ebay_rest` 库本身不提供自动获取初始 Token 的功能，我们需要手动完成标准的 OAuth 2.0 授权码模式流程。这需要借助一个名为 `ngrok` 的工具来创建一个临时的、安全的 HTTPS 通道，以满足 eBay 的安全要求。

---

## 准备工作 (仅需做一次)

1.  **下载 ngrok**:
    - 前往 ngrok 官网下载页面: [https://ngrok.com/download](https://ngrok.com/download)
    - 下载对应您操作系统的版本，它是一个独立的可执行文件，无需安装。

2.  **关联 ngrok 账户**:
    - 在 ngrok 官网注册一个免费账户。
    - 登录后，在 Dashboard 页面找到您的 `authtoken`。
    - 打开终端，进入 ngrok 所在的目录，运行一次性关联命令：
      ```bash
      ngrok config add-authtoken <你的TOKEN_HERE>
      ```

---

## Token 更新操作步骤

整个过程需要同时打开 **3个** 终端窗口。

### 步骤 1: 启动 ngrok 安全通道 (终端 1)

这是第一步，为我们的本地服务器创建一个 eBay 认可的公开 HTTPS 地址。

1.  打开 **第一个终端**。
2.  运行以下命令，启动 ngrok 并将其转发到我们本地的 8000 端口：
    ```bash
    ngrok http 8000
    ```
3.  ngrok 启动后，会显示一个 `Forwarding` 地址，例如：
    ```
    Forwarding      https://<一串随机字符>.ngrok-free.app -> http://localhost:8000
    ```
4.  **复制这个 `https://` 开头的完整地址**。这是我们接下来需要用到的安全回调地址 (Redirect URI)。
5.  **保持这个终端窗口一直打开，不要关闭**。

### 步骤 2: 更新 eBay 后台配置

现在，我们需要告诉 eBay 这个新的、临时的回调地址是合法的。

1.  登录您的 [eBay 开发者账户](https://developer.ebay.com/my/keys)。
2.  找到您的应用程序，进入 "User Tokens" 设置。
3.  找到您的 **RuName (Redirect URI name)** 配置。
4.  将 "Accept redirect URL" 的值**更新为您刚刚从 ngrok 复制的那个 `https://` 地址**，并在末尾加上斜杠 `/`。
    - 例如: `https://<一串随机字符>.ngrok-free.app/`
5.  保存设置。

### 步骤 3: 启动本地捕获服务器 (终端 2)

这个服务器将等待 eBay 将用户的浏览器跳转回来，并从中捕获授权码。

1.  打开 **第二个终端**。
2.  进入本项目目录，运行 `capture_code.py` 脚本：
    ```bash
    python capture_code.py
    ```
3.  脚本会显示服务器已在 `http://localhost:8000` 启动，并等待 eBay 的回调。
4.  **保持这个终端窗口也一直打开**。

### 步骤 4: 触发浏览器授权流程

这一步的目的是打开浏览器，让您作为账户所有者登录并授权。

1.  打开 **第三个终端**。
2.  进入本项目目录，运行一个能触发 `ebay_rest` 库进行授权的简单脚本（例如，一个只有 `from ebay_rest import API; api = API(path='.', ...)` 的脚本）。
3.  浏览器会自动打开 eBay 的登录和授权页面。请完成登录并点击 "Agree" 或 "同意"。

### 步骤 5: 获取授权码并交换 Token

这是收获成果的时刻。

1.  **捕获授权码**:
    - 当您在浏览器中授权成功后，浏览器页面会跳转到 ngrok 的地址。
    - 此时，请切换回您运行着 `capture_code.py` 的**第二个终端**。您会看到脚本已经成功打印出了捕获到的一长串**授权码 (Authorization Code)**。
    - **复制这个授权码**。

2.  **交换 Refresh Token**:
    - 打开 `exchange_code.py` 文件。
    - 将 `AUTH_CODE` 变量的值更新为您刚刚复制的授权码。
    - 确保 `REDIRECT_URI` 变量的值也是您当前 ngrok 的 `https://` 地址。
    - 回到您的**第三个终端**，运行 `exchange_code.py` 脚本：
      ```bash
      python exchange_code.py
      ```
    - 脚本会向 eBay 服务器发起请求，并成功打印出包含 `refresh_token` 和 `refresh_token_expiry` 的 JSON 数据。

### 步骤 6: 更新配置文件 (关键步骤)

这是最后一步，也是最需要注意细节的一步。

1.  **转换 Expiry 时间格式 (重要！)**
    - `exchange_code.py` 脚本输出的 `refresh_token_expiry` 是一个**时长（秒数）**，例如 `47304000`。
    - **不可以直接**将这个数字粘贴到配置文件中，否则会引发格式错误。
    - 运行我们准备好的辅助脚本 `calculate_expiry.py` (如果需要，请将 `SECONDS_TO_EXPIRY` 的值更新为最新获取的秒数)，它会将秒数转换为 eBay 要求的**绝对时间字符串**。
      ```bash
      python calculate_expiry.py
      ```
    - 脚本会输出类似 `2027-03-14T07:06:14.000Z` 的字符串。**请复制这个字符串**。

2.  **粘贴 Token 和 Expiry 到 JSON 文件**
    - 打开 `ebay_rest.json` 文件。
    - **仔细并完整地**复制 `exchange_code.py` 输出的 `refresh_token` 值，粘贴到 `token` 对象的 `refresh_token` 字段。
    - 将上一步**计算出的时间字符串**粘贴到 `refresh_token_expiry` 字段。
    - 确保 `refresh_token_expiry` 的值是一个**带引号的字符串**，而不是数字。

    修改后的 `"token"` 对象应如下所示：
    ```json
    "token": {
        "refresh_token": "v^1.1#i^1#... (这里是您新获取的完整Token)",
        "refresh_token_expiry": "2027-03-14T07:06:14.000Z"
    }
    ```

3.  **保存文件**。

**恭喜！** 您已成功更新 Refresh Token。现在您可以关闭所有终端窗口，您的主业务程序又可以在接下来的一年半时间里自动运行了。

---

## 附录：常见问题排查 (FAQ)

- **Q: 遇到 `Error 98004 is date time string formatting error` 错误怎么办?**
  **A:** 这是因为您将 `refresh_token_expiry` 的值直接填成了秒数（如 `47304000`），而没有将其转换为 `YYYY-MM-DDTHH:MM:SS.sssZ` 格式的字符串。请严格按照**步骤 6.1** 进行转换。

- **Q: 遇到 `Error 96011 is the provided authorization refresh token is invalid` 错误怎么办?**
  **A:** 有两个主要原因：
    1.  **Token 复制不完整**: `refresh_token` 字符串非常长，请确保从头到尾、不带任何多余空格地完整复制。
    2.  **App ID 不匹配**: 请确保您在 `ebay_rest.json` 中配置的 `appid` 和 `certid`，与您在 `exchange_code.py` 中用来生成 Token 的 `APP_ID` 和 `CERT_ID` 是完全一致的。