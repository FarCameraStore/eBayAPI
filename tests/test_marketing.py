# -*- coding: utf-8 -*-
"""
测试 eBay Marketing API (Promoted Listings) 功能
包括：
1. 获取所有推广活动
2. 为推广活动添加商品
3. 查看所有商品推广状态并交互式添加
"""

import sys
import os
from datetime import datetime

# 添加父目录到路径以便导入 ebayapi 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ebayapi.ebayapi import EbayAPI


def test_get_all_campaigns():
    """测试获取所有推广活动"""
    print("=" * 80)
    print("测试1: 获取所有推广活动")
    print("=" * 80)
    
    # 初始化 API 客户端
    api = EbayAPI(
        application='FarThings',
        user='FarCamera',
        config_path='ebay_rest.json'
    )
    
    # 获取所有活动
    print("\n1.1 获取所有推广活动（不带筛选）")
    result = api.get_all_campaigns(limit=10)
    
    total_campaigns = result.get('total', 0)
    campaigns_list = result.get('campaigns', [])
    
    if campaigns_list:
        print(f"\n找到 {total_campaigns} 个推广活动，显示前 {len(campaigns_list)} 个：\n")
        for i, campaign in enumerate(campaigns_list, 1):
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
                budget = campaign.get('budget', {})
                if budget:
                    daily_budget = budget.get('daily', {})
                    if daily_budget:
                        daily_amount = daily_budget.get('amount', {})
                        print(f"  - 每日预算: {daily_amount.get('value', 'N/A')} {daily_amount.get('currency', '')}")
            
            # 显示时间信息
            start_date = campaign.get('startDate', 'N/A')
            end_date = campaign.get('endDate', 'N/A')
            print(f"  - 开始时间: {start_date}")
            print(f"  - 结束时间: {end_date}")
            print()
    else:
        print(f"\n未找到任何推广活动（API 返回总数: {total_campaigns}）")
        if 'error' in result:
            print(f"错误: {result['error']}")
    
    # 测试带筛选条件的查询
    print("\n1.2 获取正在运行的推广活动（RUNNING）")
    result_running = api.get_all_campaigns(campaign_status='RUNNING', limit=5)
    running_count = result_running.get('total', 0)
    running_campaigns = result_running.get('campaigns', [])
    print(f"找到 {running_count} 个正在运行的活动，返回 {len(running_campaigns)} 个")
    
    print("\n1.3 获取使用 CPS 模式的推广活动")
    result_cps = api.get_all_campaigns(funding_strategy='COST_PER_SALE', limit=5)
    cps_count = result_cps.get('total', 0)
    cps_campaigns = result_cps.get('campaigns', [])
    print(f"找到 {cps_count} 个使用 COST_PER_SALE 模式的活动，返回 {len(cps_campaigns)} 个")
    
    return result


def test_add_items_to_campaign(campaign_id=None):
    """测试为推广活动添加商品"""
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
    
    # 准备要添加的商品列表（请替换为实际的商品ID）
    items = [
        {
            'inventory_reference_id': '123456789012',
            'inventory_reference_type': 'INVENTORY_ITEM',
            'bid_percentage': '10.0'
        },
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


def test_listing_promotion_status():
    """测试商品推广状态查询和添加功能"""
    print("\n" + "=" * 80)
    print("测试3: 商品推广状态管理")
    print("=" * 80)
    
    # 初始化 API 客户端
    api = EbayAPI(
        application='FarThings',
        user='FarCamera',
        config_path='ebay_rest.json'
    )
    
    # 获取所有推广活动
    print("\n正在获取推广活动...")
    campaigns_result = api.get_all_campaigns(campaign_status='RUNNING')
    campaigns = campaigns_result.get('campaigns', [])
    
    if not campaigns:
        print("没有找到正在运行的推广活动")
        return
    
    # 收集所有活动中的商品ID
    all_promoted_ids = set()
    campaign_ads_map = {}
    
    print(f"\n找到 {len(campaigns)} 个正在运行的推广活动")
    for campaign in campaigns:
        campaign_id = campaign.get('campaignId')
        campaign_name = campaign.get('campaignName')
        print(f"  - 获取活动 '{campaign_name}' (ID: {campaign_id}) 的商品...")
        
        ads_result = api.get_campaign_ads(campaign_id, debug=False)
        inventory_ids = ads_result.get('inventory_ids', set())
        listing_ids = ads_result.get('listing_ids', set())
        
        # 确保所有 ID 都是字符串格式
        inventory_ids_str = {str(id) for id in inventory_ids if id}
        listing_ids_str = {str(id) for id in listing_ids if id}
        
        campaign_ads_map[campaign_id] = {
            'name': campaign_name,
            'inventory_ids': inventory_ids_str,
            'listing_ids': listing_ids_str,
            'total': ads_result.get('total', 0)
        }
        all_promoted_ids.update(inventory_ids_str)
        all_promoted_ids.update(listing_ids_str)
        
        print(f"    {ads_result.get('total', 0)} 个广告")
    
    # 获取所有在售商品
    print("\n正在获取所有在售商品...")
    active_listings = api.get_active_listings()
    
    if not active_listings:
        print("未找到在售商品")
        return
    
    # 分类商品：已推广 vs 未推广
    promoted_listings = []
    unpromoted_listings = []
    
    for listing in active_listings:
        item_id = listing.get('ItemID')
        sku = listing.get('SKU')
        
        # 确保 item_id 是字符串格式
        identifier = str(item_id) if item_id else (str(sku) if sku else None)
        
        if identifier and identifier in all_promoted_ids:
            promoted_listings.append(listing)
        else:
            unpromoted_listings.append(listing)
    
    # 显示统计信息
    print("\n" + "=" * 80)
    print("商品推广状态统计")
    print("=" * 80)
    print(f"总在售商品: {len(active_listings)}")
    print(f"已推广商品: {len(promoted_listings)}")
    print(f"未推广商品: {len(unpromoted_listings)}")
    
    # 显示未推广的商品列表
    if unpromoted_listings:
        print("\n" + "-" * 80)
        print("未推广的商品列表:")
        print("-" * 80)
        max_display = min(50, len(unpromoted_listings))
        for i, listing in enumerate(unpromoted_listings[:max_display], 1):
            item_id = listing.get('ItemID', 'N/A')
            title = listing.get('Title', 'N/A')
            price = listing.get('SellingStatus', {}).get('CurrentPrice', {}).get('value', 'N/A')
            currency = listing.get('SellingStatus', {}).get('CurrentPrice', {}).get('_currencyID', '')
            sku = listing.get('SKU', 'N/A')
            
            # 单行显示：序号. 标题 | ID: xxx | SKU: xxx | 价格: xxx
            title_display = title[:40] if len(title) > 40 else title
            print(f"{i:2d}. {title_display:<42} | ID: {item_id:<14} | SKU: {sku:<16} | ${price}")
        
        if len(unpromoted_listings) > max_display:
            print(f"\n... 还有 {len(unpromoted_listings) - max_display} 个未推广的商品未显示")
    
    # 交互式添加到推广活动
    if unpromoted_listings and campaigns:
        print("\n" + "=" * 80)
        print("添加商品到推广活动")
        print("=" * 80)
        
        try:
            choice = input("\n是否要将商品添加到推广活动？(y/n): ").strip().lower()
            if choice == 'y':
                # 选择商品
                print("\n选择要添加的商品:")
                print("输入商品序号，支持:")
                print("  - 单个: 1")
                print("  - 多个: 1,3,5")
                print("  - 范围: 5-10")
                print("  - 混合: 1,3,5-10,15")
                print("  - 全部: all")
                
                items_input = input("\n请输入: ").strip()
                
                selected_listings = []
                if items_input.lower() == 'all':
                    selected_listings = unpromoted_listings
                else:
                    # 解析输入（支持逗号分隔和范围）
                    selected_indices = set()
                    parts = items_input.split(',')
                    
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            # 范围选择，如 5-10
                            try:
                                start, end = part.split('-')
                                start_idx = int(start.strip()) - 1
                                end_idx = int(end.strip()) - 1
                                for idx in range(start_idx, end_idx + 1):
                                    if 0 <= idx < len(unpromoted_listings):
                                        selected_indices.add(idx)
                            except ValueError:
                                print(f"⚠️  无效的范围格式: {part}")
                        else:
                            # 单个选择
                            try:
                                idx = int(part) - 1
                                if 0 <= idx < len(unpromoted_listings):
                                    selected_indices.add(idx)
                            except ValueError:
                                print(f"⚠️  无效的序号: {part}")
                    
                    selected_listings = [unpromoted_listings[i] for i in sorted(selected_indices)]
                
                if not selected_listings:
                    print("未选择任何商品")
                    return
                
                print(f"\n已选择 {len(selected_listings)} 个商品")
                
                # 选择推广活动
                print("\n可用的推广活动:")
                for i, campaign in enumerate(campaigns, 1):
                    campaign_name = campaign.get('campaignName')
                    campaign_id = campaign.get('campaignId')
                    funding_model = campaign.get('fundingStrategy', {}).get('fundingModel', 'N/A')
                    ads_count = campaign_ads_map.get(campaign_id, {}).get('total', 0)
                    print(f"{i}. {campaign_name} ({funding_model}) - {ads_count} 个商品")
                
                campaign_idx = input(f"\n选择推广活动 (1-{len(campaigns)}): ").strip()
                try:
                    campaign_idx = int(campaign_idx) - 1
                    if 0 <= campaign_idx < len(campaigns):
                        selected_campaign = campaigns[campaign_idx]
                        campaign_id = selected_campaign.get('campaignId')
                        campaign_name = selected_campaign.get('campaignName')
                        funding_strategy = selected_campaign.get('fundingStrategy', {})
                        funding_model = funding_strategy.get('fundingModel')
                        
                        # 准备商品数据
                        items = []
                        
                        # CPS 模式需要广告费率
                        if funding_model == 'COST_PER_SALE':
                            # 获取Campaign的默认广告费率
                            campaign_default_bid = funding_strategy.get('bidPercentage', '10.0')
                            bid_percentage = input(f"\n输入广告费率 (%) [默认 {campaign_default_bid}]: ").strip()
                            default_bid = bid_percentage if bid_percentage else campaign_default_bid
                        
                        for listing in selected_listings:
                            item_id = listing.get('ItemID')
                            item = {
                                'listing_id': item_id  # Trading API 使用 listing_id
                            }
                            
                            if funding_model == 'COST_PER_SALE':
                                item['bid_percentage'] = default_bid
                            
                            items.append(item)
                        
                        # 执行添加 (use_listing_id=True 表示使用 Trading API 的 listing ID)
                        print(f"\n正在添加 {len(items)} 个商品到推广活动 '{campaign_name}'...")
                        result = api.add_items_to_campaign(campaign_id, items, use_listing_id=True)
                        
                        if result.get('success'):
                            print(f"\n✅ 成功添加所有商品!")
                            print(f"总计: {result['total_succeeded']}/{result['total_requested']} 成功")
                        else:
                            print(f"\n⚠️  部分或全部商品添加失败")
                            print(f"成功: {result.get('total_succeeded', 0)}/{result.get('total_requested', 0)}")
                            
                            # 显示失败详情
                            if result.get('responses'):
                                print("\n详细结果:")
                                for resp in result['responses']:
                                    # 兼容两种API格式和命名风格（camelCase vs snake_case）
                                    item_id = (resp.get('listingId') or resp.get('listing_id') or 
                                             resp.get('inventoryReferenceId') or resp.get('inventory_reference_id') or 'Unknown')
                                    status = resp.get('statusCode') or resp.get('status_code')
                                    
                                    if status in [200, 201]:
                                        ad_id = resp.get('adId') or resp.get('ad_id') or 'N/A'
                                        print(f"  ✅ {item_id} -> Ad ID: {ad_id}")
                                    else:
                                        errors = resp.get('errors', [])
                                        error_msg = errors[0].get('message', 'Unknown') if errors else 'Unknown'
                                        print(f"  ❌ {item_id}: {error_msg}")
                    else:
                        print("无效的活动序号")
                except (ValueError, IndexError) as e:
                    print(f"输入错误: {e}")
        except KeyboardInterrupt:
            print("\n\n操作已取消")


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("eBay Marketing API (Promoted Listings) 测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试1: 获取所有推广活动
        campaigns_result = test_get_all_campaigns()
        
        print("\n" + "=" * 80)
        print("推广活动总结")
        print("=" * 80)
        
        campaigns_list = campaigns_result.get('campaigns', [])
        total = campaigns_result.get('total', 0)
        
        if campaigns_list:
            print(f"\n共找到 {total} 个推广活动，显示 {len(campaigns_list)} 个：\n")
            for i, campaign in enumerate(campaigns_list, 1):
                campaign_name = campaign.get('campaignName', 'N/A')
                campaign_id = campaign.get('campaignId', 'N/A')
                campaign_status = campaign.get('campaignStatus', 'N/A')
                funding_model = campaign.get('fundingStrategy', {}).get('fundingModel', 'N/A')
                
                print(f"{i}. {campaign_name}")
                print(f"   ID: {campaign_id}")
                print(f"   状态: {campaign_status}")
                print(f"   资金模式: {funding_model}")
        else:
            print(f"\n未找到推广活动（总数: {total}）")

        # 测试2: 为推广活动添加商品（演示模式）
        # test_add_items_to_campaign()
        
        # 测试3: 商品推广状态管理（交互式）
        test_listing_promotion_status()
        
        print("\n" + "=" * 80)
        print("测试完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
