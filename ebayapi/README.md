# ebayapi/README.md

# ebayapi

一个面向对象的 eBay Trading API 封装包，支持订单、商品、发货等常用操作。

## 安装

```bash
pip install .
```

## 使用示例

```python
from ebayapi import EbayAPI
api = EbayAPI(application, user, config_path)
orders = api.get_orders_last_days(days=7)
```

## 依赖
- ebaysdk
- ebay_rest

## 许可证
MIT
