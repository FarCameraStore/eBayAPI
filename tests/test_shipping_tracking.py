#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运单号上传功能
"""

import sys
import os
from datetime import datetime, timezone

from ebayapi import EbayAPI

def test_upload_shipping_tracking():
    """
    测试上传运单号功能
    """
    # 初始化eBay API客户端
    api_client = EbayAPI(
        application='FarThings',  # 根据你的配置文件修改
        user='FarCamera',         # 根据你的配置文件修改
        config_path='ebay_rest.json'  # 配置文件路径
    )
    
    print("=== eBay 运单号上传功能测试 ===\n")
    
    # 测试用例1: 使用订单ID上传跟踪信息
    print("测试用例1: 使用订单ID上传完整跟踪信息")
    order_id = "20-13614-33225"  # 替换为实际的订单ID
    tracking_number = "6102040901903675"  # 替换为实际的跟踪号
    shipping_carrier = "DHL eCommerce America"  # 承运商
    
    result = api_client.upload_shipping_tracking_info(
        order_id=order_id,
        tracking_number=tracking_number,
        shipping_carrier=shipping_carrier,
        shipped_time=datetime.now(timezone.utc),
        is_paid=True,
        is_shipped=True
    )
    
    return result


if __name__ == "__main__":
    try:
        test_upload_shipping_tracking()
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()