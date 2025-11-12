# -*- coding: utf-8 -*-
"""
测试向买家发送消息功能
使用 AddMemberMessageAAQToPartner API
"""

import sys
import os
from datetime import datetime

# 添加父目录到路径以便导入 ebayapi 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ebayapi.ebayapi import EbayAPI


def test_send_basic_message():
    """
    测试基本消息发送功能
    """
    print("=" * 80)
    print("测试 1: 发送基本感谢消息")
    print("=" * 80)
    
    # 初始化 API 客户端
    api = EbayAPI(
        application='FarThings',
        user='FarCamera',
        config_path='ebay_rest.json'
    )
    
    # 测试参数 - 请根据实际情况修改这些值
    item_id = '389180132170'  # 替换为实际的商品ID
    recipient_id = 'q7o_9sb6r76'  # 替换为实际的买家用户名
    
    message_body = '''
Thank you for your purchase! We appreciate your support and want to ensure you have the best possible experience. However, we regret to inform you that we are currently unable to provide reliable and stable used batteries. To ensure the best experience, we will separately purchase a brand-new compatible camera battery for you using your address via a U.S.-based platform. The battery and camera should arrive around the same time. We apologize for any inconvenience and thank you for your understanding! I will send the camera to you very soon.
'''

    result = api.send_message_to_buyer(
        item_id=item_id,
        recipient_id=recipient_id,
        subject='Notice Regarding Battery for Your Recent Purchase',
        message_body=message_body,
        question_type='General',
        email_copy_to_sender=False
    )
    
    print("\n结果:")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  响应: {result.get('response', {}).get('Ack', 'N/A')}")
        if 'warnings' in result:
            print(f"  警告: {result['warnings']}")
    else:
        print(f"  错误: {result.get('error', 'Unknown error')}")
    
    return result


def main():
    """
    主测试函数
    """
    print("eBay 发送消息 API 测试")
    print("=" * 80)
    print("\n注意事项:")
    print("1. 在运行测试前，请确保修改了正确的 item_id 和 recipient_id")
    print("2. 调用者必须是该商品的买家或卖家")
    print("3. API 有速率限制：每个用户ID在60秒内最多调用75次")
    print("4. 买卖双方可在订单创建后90天内发送消息")
    print("5. 该API在Sandbox环境不支持测试")
    print("\n" + "=" * 80)
    
    # 选择要运行的测试
    print("\n请选择要运行的测试:")
    print("  1. 测试基本运输消息")
    print("  0. 退出")
    
    choice = input("\n请输入选项 (0-7): ").strip()
    
    try:
        if choice == '1':
            test_send_basic_message()
        elif choice == '0':
            print("\n退出测试")
            return
        else:
            print("\n无效的选项")
            return
        
        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
