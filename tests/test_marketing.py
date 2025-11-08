# -*- coding: utf-8 -*-
"""
测试 eBay Marketing API (Promoted Listings) 功能
包括：
1. 获取所有推广活动
2. 为推广活动添加商品
"""

import sys
import os
from datetime import datetime

# 添加父目录到路径以便导入 ebayapi 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ebayapi.ebayapi import EbayAPI


def test_get_all_campaigns():
    """
    测试获取所有推广活动
    """
    print("=" * 80)
    print("测试1: 获取所有推广活动")
    print("=" * 80)
    
    # 初始化 API 客户端
    api = EbayAPI(
        application='FarThings',  # 根据你的配置文件修改
        user='FarCamera',         # 根据你的配置文件修改
        config_path='ebay_rest.json'  # 配置文件路径
    )
    
    # 获取所有活动
    print("\n1.1 获取所有推广活动（不带筛选）")
    result = api.get_all_campaigns(limit=10)
    
    if result.get('campaigns'):
        print(f"\n找到 {result['total']} 个推广活动，显示前 {len(result['campaigns'])} 个：\n")
        for i, campaign in enumerate(result['campaigns'], 1):
            print(f"活动 {i}:")
            print(f"  - ID: {campaign.get('campaignId')}")
            print(f"  - 名称: {campaign.get('campaignName')}")
            print(f"  - 状态: {campaign.get('campaignStatus')}")
            print(f"  - 市场: {campaign.get('marketplaceId')}")
            
            # 显示资金策略
            funding_strategy = campaign.get('fundingStrategy', {})
            funding_model = funding_strategy.get('fundingModel', 'Unknown')
            print(f"  - 资金模式: {funding_model}")
            
            if funding_model == 'COST_PER_SALE':
                bid_percentage = funding_strategy.get('bidPercentage', 'N/A')
                print(f"  - 广告费率: {bid_percentage}%")
            elif funding_model == 'COST_PER_CLICK':
                budget = campaign.get('budget', {}).get('daily', {})
                daily_amount = budget.get('amount', {})
                print(f"  - 每日预算: {daily_amount.get('value', 'N/A')} {daily_amount.get('currency', '')}")
            
            # 显示时间信息
            start_date = campaign.get('startDate', 'N/A')
            end_date = campaign.get('endDate', 'N/A')
            print(f"  - 开始时间: {start_date}")
            print(f"  - 结束时间: {end_date}")
            print()
    else:
        print("未找到任何推广活动")
        if 'error' in result:
            print(f"错误: {result['error']}")
    
    # 测试带筛选条件的查询
    print("\n1.2 获取正在运行的推广活动（RUNNING）")
    result = api.get_all_campaigns(campaign_status='RUNNING', limit=5)
    print(f"找到 {result.get('total', 0)} 个正在运行的活动")
    
    print("\n1.3 获取使用 CPS 模式的推广活动")
    result = api.get_all_campaigns(funding_strategy='COST_PER_SALE', limit=5)
    print(f"找到 {result.get('total', 0)} 个使用 COST_PER_SALE 模式的活动")
    
    return result


def test_add_items_to_campaign(campaign_id=None):
    """
    测试为推广活动添加商品
    
    参数:
        campaign_id (str): 要添加商品的活动ID，如果不提供则尝试获取第一个活动
    """
    print("\n" + "=" * 80)
    print("测试2: 为推广活动添加商品")
    print("=" * 80)
    
    # 初始化 API 客户端
    api = EbayAPI(
        application='production',
        user='farcamerastore',
        config_path='ebay_rest.json',
        marketplace_id='EBAY_US'
    )
    
    # 如果没有提供 campaign_id，尝试获取第一个活动
    if not campaign_id:
        print("\n未提供活动ID，正在获取第一个可用的活动...")
        campaigns_result = api.get_all_campaigns(campaign_status='RUNNING', limit=1)
        
        if campaigns_result.get('campaigns'):
            campaign_id = campaigns_result['campaigns'][0].get('campaignId')
            campaign_name = campaigns_result['campaigns'][0].get('campaignName')
            print(f"将使用活动: {campaign_name} (ID: {campaign_id})")
        else:
            print("错误: 未找到任何正在运行的活动")
            return None
    
    # 准备要添加的商品列表
    # 注意：请替换为你实际的商品ID/SKU
    items = [
        {
            'inventory_reference_id': '123456789012',  # 替换为实际的 Item ID
            'inventory_reference_type': 'INVENTORY_ITEM',
            'bid_percentage': '10.0'  # CPS模式需要，10% 广告费率
        },
        # 取消注释以添加更多商品
        # {
        #     'inventory_reference_id': 'SKU-ABC-123',  # 或使用 SKU
        #     'inventory_reference_type': 'INVENTORY_ITEM',
        #     'bid_percentage': '12.5'
        # },
    ]
    
    print(f"\n准备添加 {len(items)} 个商品到活动 {campaign_id}")
    print("\n注意: 此示例使用的是演示数据，请替换为实际的商品ID")
    print("如需实际执行，请取消下面的注释并提供真实的商品ID\n")
    
    # 取消下面的注释以实际执行添加操作
    # result = api.add_items_to_campaign(campaign_id, items)
    # 
    # if result.get('success'):
    #     print(f"\n✅ 成功添加所有商品!")
    #     print(f"总计: {result['total_succeeded']}/{result['total_requested']} 成功")
    # else:
    #     print(f"\n⚠️ 部分或全部商品添加失败")
    #     print(f"成功: {result.get('total_succeeded', 0)}/{result.get('total_requested', 0)}")
    #     
    #     # 显示详细结果
    #     if result.get('responses'):
    #         print("\n详细结果:")
    #         for resp in result['responses']:
    #             inv_id = resp.get('inventoryReferenceId')
    #             status = resp.get('statusCode')
    #             
    #             if status == 201:
    #                 ads = resp.get('ads', [])
    #                 if ads:
    #                     ad_id = ads[0].get('adId')
    #                     print(f"  ✅ {inv_id} -> Ad ID: {ad_id}")
    #             else:
    #                 errors = resp.get('errors', [])
    #                 error_msg = errors[0].get('message', 'Unknown') if errors else 'Unknown'
    #                 print(f"  ❌ {inv_id} -> {error_msg}")
    
    print("演示模式：实际添加代码已注释，请根据需要取消注释")
    
    return None


def main():
    """
    主测试函数
    """
    print("\n" + "=" * 80)
    print("eBay Marketing API (Promoted Listings) 测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试1: 获取所有推广活动
        campaigns_result = test_get_all_campaigns()
        
        print("\n" + "=" * 80)
        print("Campaigns ：")
        for campaign in campaigns_result.get('campaigns', []):
            print(f" - {campaign.get('campaignName')} (ID: {campaign.get('campaignId')})")

        # 测试2: 为推广活动添加商品（演示模式）
        # 如果想测试添加商品，可以提供一个有效的 campaign_id
        # test_add_items_to_campaign(campaign_id='your_campaign_id_here')
        # test_add_items_to_campaign()
        
        print("\n" + "=" * 80)
        print("测试完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
