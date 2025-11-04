#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eBay 需要发货订单获取测试脚本（简化版）

这个脚本测试简化后的订单获取功能，只使用 get_orders_requiring_shipment 函数。
"""

import sys
import os
from datetime import datetime, timezone

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ebayapi.ebayapi import EbayAPI

def test_orders():
    """测试需要发货的订单获取功能"""
    
    print("=" * 60)
    print("eBay 需要发货订单获取测试（简化版）")
    print("=" * 60)

    # 初始化API客户端
    print("正在初始化eBay API客户端...")
    api = EbayAPI(
        application='FarThings',
        user='FarCamera',
        config_path='ebay_rest.json',
        marketplace_id='EBAY_US'
    )
    print("API客户端初始化成功!")
    
    # 测试获取需要发货的订单
    print("\n" + "=" * 40)
    print("获取需要发货的订单")
    print("=" * 40)
    
    days = 1
    
    orders = api.get_orders_last_days(days=days)
    order = orders[0]
    trans = api.get_transactions_for_order(order.get('OrderID'), order_date=order.get('TransactionArray').get('Transaction')[0].get('CreatedDate'))
    for tx in trans:
        print(tx)

if __name__ == "__main__":
    test_orders()