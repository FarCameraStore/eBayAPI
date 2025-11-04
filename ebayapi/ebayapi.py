# -*- coding: utf-8 -*-
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from ebay_rest import API, Error
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

from datetime import datetime, timezone, timedelta
from dateutil import parser

class EbayAPI:
    """
    eBay API 客户端，统一管理 REST 和 Trading API 的连接。
    支持订单、交易、商品刊登等常用操作。
    """

    def __init__(self, application: str, user: str, config_path: str, marketplace_id: str = 'EBAY_US'):
        """
        初始化 EbayAPI 类，加载配置并创建 API 客户端。
        """
        self.application = application
        self.user = user
        self.config_path = config_path
        self.marketplace_id = marketplace_id
        self._load_config()

        self.access_token = None
        self.api_rest = None
        self.api_trading = None
        
        # 在构造函数中统一初始化所有 API 客户端
        self._initialize_apis()

    def _load_config(self):
        """
        从配置文件加载应用和用户信息。
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.app_info = config['applications'][self.application]
        self.user_info = config['users'][self.user]
        self.APP_ID = self.app_info['app_id']
        self.DEV_ID = self.app_info['dev_id']
        self.CERT_ID = self.app_info['cert_id']
    
    def _initialize_apis(self):
        """
        初始化 REST 和 Trading API 客户端。
        获取 access_token 并创建 API 实例。
        """
        try:
            print("正在初始化 eBay REST API 客户端...")
            self.api_rest = API(path='.', application=self.application, user=self.user, header='US')
            # 获取 access_token 以供 Trading API 使用
            self.access_token = self.api_rest._user_token.get()
            if not self.access_token:
                print("通过 REST API 客户端获取 access_token 失败。", file=sys.stderr)
                return

            print("正在初始化 eBay Trading API 客户端...")
            self.api_trading = Trading(
                token=self.access_token,
                config_file=None,
                appid=self.APP_ID,
                devid=self.DEV_ID,
                certid=self.CERT_ID,
                siteid='0',
                environment='production'
            )
            print("API 客户端初始化成功。")

        except Error as e:
            print(f"初始化 REST API 客户端失败: {e}", file=sys.stderr)
        except ConnectionError as e:
            print(f"初始化 Trading API 客户端失败: {e}", file=sys.stderr)
        except Exception as e:
            print(f"API 初始化过程中发生未知错误: {e}", file=sys.stderr)


    def get_transactions_for_order(self, order_id: str, order_date: datetime, days_window: int = 2) -> list:
        """
        获取指定订单ID的所有交易信息。
        以 order_date 为中心，搜索前后 days_window 天范围内的交易。
        参数：
            order_id: 订单ID
            order_date: 订单时间（datetime对象）
            days_window: 搜索窗口天数
        返回：交易信息列表
        """
        if not self.api_rest:
            print("REST API 客户端未初始化，无法查询交易信息。", file=sys.stderr)
            return []

        # 验证 order_date 必须是 datetime 对象
        if not isinstance(order_date, datetime):
            error_msg = f"错误: order_date 必须是 datetime 对象，实际类型: {type(order_date)}"
            print(error_msg, file=sys.stderr)
            raise TypeError(error_msg)
        
        # # 确保 datetime 对象有时区信息，如果没有则假定为 UTC
        # if order_date.tzinfo is None:
        #     dt_utc = order_date.replace(tzinfo=timezone.utc)
        #     print(f"订单时间无时区信息，假定为UTC: {order_date} -> {dt_utc}")
        # else:
        #     # 转换为 UTC 时区
        #     dt_utc = order_date.astimezone(timezone.utc)
        #     print(f"订单时间转换为UTC: {order_date} -> {dt_utc}")
        
        # print(f"成功处理订单时间: {dt_utc}")

        # 计算查询窗口
        date_from = order_date - timedelta(days=days_window)
        date_to = order_date + timedelta(days=days_window)

        # 格式化为 Zulu (UTC) 格式
        date_from_zulu = date_from.strftime('%Y-%m-%dT%H:%M:%SZ')
        date_to_zulu = date_to.strftime('%Y-%m-%dT%H:%M:%SZ')

        filter_query = f"transactionDate:[{date_from_zulu}..{date_to_zulu}]"
        print(f"生成的 API 查询过滤器: {filter_query}")

        try:
            response = self.api_rest.sell_finances_get_transactions(filter=filter_query, x_ebay_c_marketplace_id=self.marketplace_id)
    
            all_transactions = list(response)
            if not all_transactions:
                return []

            # 筛选与订单ID相关的交易
            order_transactions = []
            print(f"正在从 {len(all_transactions)} 条记录中筛选与订单ID '{order_id}' 相关的交易...")

            for tx_wrapper in all_transactions:
                record = tx_wrapper.get('record')
                if not isinstance(record, dict):
                    continue

                found_order_id = record.get('order_id')
                if not found_order_id:
                    references = record.get('references', [])
                    if isinstance(references, list):
                        for ref in references:
                            if isinstance(ref, dict) and ref.get('reference_type') == 'ORDER_ID':
                                found_order_id = ref.get('reference_id')
                                break

                if found_order_id == order_id:
                    order_transactions.append(record)

            if not order_transactions:
                print(f"成功查询交易，但未找到与订单 {order_id} 相关的交易信息。")
            else:
                print(f"已找到 {len(order_transactions)} 条与订单 {order_id} 相关的交易记录。")

            return order_transactions

        except Exception as e:
            print(f"调用 API 或处理数据时发生错误: {e}", file=sys.stderr)
            return []

    def check_order_advertising_fees(self, order_id: str, order_date: datetime, days_window: int = 2) -> dict:
        """
        检查指定订单是否有相关的广告费扣款。
        
        参数:
            order_id: 订单ID
            order_date: 订单时间（datetime对象）
            days_window: 搜索窗口天数，默认前后2天
            
        返回:
            dict: 广告费信息，包含是否有广告费、交易详情、金额等
        """
        # 获取订单相关的所有交易
        transactions = self.get_transactions_for_order(order_id, order_date, days_window)
        
        if not transactions:
            return {
                'has_advertising_fees': False,
                'advertising_transaction': None,
                'amount': None,
                'currency': None,
                'transaction_date': None,
                'order_id': order_id
            }
        
        # 查找广告费交易
        ad_keyword = 'Promoted Listings'
        advertising_transaction = None
        
        for transaction in transactions:
            memo = transaction.get('transaction_memo', '')
            if memo and ad_keyword in memo:
                advertising_transaction = transaction
                break
        
        # 处理结果
        if advertising_transaction:
            amount_data = advertising_transaction.get('amount', {})
            return {
                'has_advertising_fees': True,
                'advertising_transaction': advertising_transaction,
                'amount': float(amount_data.get('value', 0)),
                'currency': amount_data.get('currency'),
                'transaction_date': advertising_transaction.get('transaction_date'),
                'order_id': order_id
            }
        else:
            return {
                'has_advertising_fees': False,
                'advertising_transaction': None,
                'amount': None,
                'currency': None,
                'transaction_date': None,
                'order_id': order_id
            }

    def get_orders_last_days(self, days=7, order_status='All') -> list:
        """
        获取最近 days 天的订单列表。
        参数：days 查询天数，order_status 订单状态
        Order_status 可选值：
            - All: 所有订单
            - Active: 尚未确认付款的订单
            - Completed: 已付款 （已取消的订单也包含在内）
        返回：订单列表
        """
        if not self.api_trading:
            print("Trading API 客户端未初始化。", file=sys.stderr)
            return []
        try:
            now = datetime.now(timezone.utc)
            create_time_from = now - timedelta(days=days)
            page_number = 1
            all_orders = []
            while True:
                request = {
                    'CreateTimeFrom': create_time_from.isoformat(),
                    'CreateTimeTo': now.isoformat(),
                    'OrderStatus': order_status,
                    'Pagination': {'EntriesPerPage': 50, 'PageNumber': page_number}
                }
                response = self.api_trading.execute('GetOrders', request)
                if response.reply.Ack not in ['Success', 'Warning']:
                    print(f"GetOrders API调用失败: {response.reply.Errors[0].LongMessage}", file=sys.stderr)
                    break
                
                order_array = getattr(response.reply, 'OrderArray', None)
                if not (order_array and hasattr(order_array, 'Order')):
                    break

                for order in order_array.Order:
                    all_orders.append(self.to_dict_recursive(order))
                
                if getattr(response.reply, 'HasMoreOrders', 'false') == 'false':
                    break
                page_number += 1
            return all_orders
        except ConnectionError as e:
            print(f"GetOrders API连接或请求出错: {e.response.text if e.response else e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"处理GetOrders时发生未知错误: {e}", file=sys.stderr)
            return []

    def _is_order_unshipped(self, order: dict) -> bool:
        """
        判断订单是否未发货的内部辅助方法。
        
        参数:
            order (dict): 订单字典
            
        返回:
            bool: True表示未发货，False表示已发货
        """
        # 检查订单级别的ShippedTime字段
        if 'ShippedTime' in order and order['ShippedTime']:
            return False
        
        # 检查交易级别的发货状态
        transaction_array = order.get('TransactionArray', {})
        if isinstance(transaction_array, dict):
            transactions = transaction_array.get('Transaction', [])
            if not isinstance(transactions, list):
                transactions = [transactions]
            
            # 如果所有交易都已发货，则订单已发货
            for transaction in transactions:
                if isinstance(transaction, dict):
                    # 检查交易级别的ShippedTime
                    if 'ShippedTime' not in transaction or not transaction['ShippedTime']:
                        return True  # 发现未发货的交易项
        
        # 检查发货详情中的跟踪信息
        shipping_details = order.get('ShippingDetails', {})
        if isinstance(shipping_details, dict):
            tracking_details = shipping_details.get('ShipmentTrackingDetails', [])
            if tracking_details:
                # 如果有跟踪信息，通常表示已发货
                return False
        
        # 默认情况下，如果没有明确的发货时间，认为是未发货
        return True

    def get_orders_requiring_shipment(self, days=7) -> list:
        """
        获取需要发货的订单（状态为Completed且未发货的订单）。
        只返回已付款但尚未发货的订单，供卖家处理发货。
        
        参数:
            days (int): 查询天数，默认7天
            
        返回:
            list: 需要发货的订单列表
        """
        if not self.api_trading:
            print("Trading API 客户端未初始化。", file=sys.stderr)
            return []
        
        try:
            print(f"正在获取最近 {days} 天内需要发货的订单...")
            
            # 获取已付款订单状态的订单
            completed_orders = self.get_orders_last_days(days=days, order_status='Completed')
            orders_requiring_shipment = []
            
            for order in completed_orders:
                # 检查是否未发货且订单状态为Completed（未取消）
                if self._is_order_unshipped(order) and order.get('OrderStatus') == 'Completed':
                    orders_requiring_shipment.append(order)
            print(f"共找到 {len(orders_requiring_shipment)} 个需要发货的订单")
            return orders_requiring_shipment
            
        except Exception as e:
            print(f"获取需要发货订单时发生错误: {e}", file=sys.stderr)
            return []

    def get_active_listings(self) -> list:
        """
        获取所有在售商品列表。
        使用 get_all_listings 方法获取数据，然后筛选出在售商品。
        返回：在售商品列表
        """
        print('正在获取在售商品...')
        
        # 使用 get_all_listings 方法获取过去120天的所有商品（Coarse级别）
        all_listings = self.get_all_listings(days=120, granularity_level='Coarse')
        
        if not all_listings:
            print("未获取到任何商品数据。")
            return []
        
        # 筛选出在售商品
        active_items = []
        now = datetime.now(timezone.utc)
        
        for item_dict in all_listings:
            # 基于EndTime的状态判断逻辑
            is_active = False
            listing_details = item_dict.get('ListingDetails')
            if listing_details:
                end_time = listing_details.get('EndTime')
                if end_time:
                    # 将API返回的naive时间标记为UTC时区
                    end_time_utc = end_time.replace(tzinfo=timezone.utc)
                    # 如果结束时间晚于现在，则商品是在售状态
                    if end_time_utc > now:
                        is_active = True
            
            if is_active:
                active_items.append(item_dict)
        
        print(f"从 {len(all_listings)} 个商品中筛选出 {len(active_items)} 个在售商品。")
        return active_items

    def get_all_listings(self, days: int = 120, granularity_level: str = 'Coarse') -> list:
        """
        获取指定天数内的所有listings。
        
        参数：
            days: 要查询的天数（从当前时间向前推算）
            granularity_level: 粒度级别控制参数，可选值：
                - None: 最低数据级别，仅返回ItemID、日期和卖家信息
                - Coarse: 粗粒度，包含标题、当前价格、竞价次数、商品状态等基本信息
                - Medium: 中等粒度，在Coarse基础上增加保留价格信息
                - Fine: 细粒度，包含最高竞价者信息和运费详情，数据量约为Medium的两倍
        
        返回：商品列表
        """
        if not self.api_trading:
            print("Trading API 客户端未初始化。", file=sys.stderr)
            return []
        
        # 验证 granularity_level 参数
        valid_granularity_levels = [None, 'Coarse', 'Medium', 'Fine']
        
        if granularity_level not in valid_granularity_levels:
            print(f"无效的GranularityLevel参数: {granularity_level}", file=sys.stderr)
            print(f"有效值包括: {', '.join([str(x) for x in valid_granularity_levels])}", file=sys.stderr)
            return []
        
        try:
            page_number = 1
            all_listings = []
            
            now = datetime.now(timezone.utc)
            start_time_from = now - timedelta(days=days)
            
            granularity_desc = granularity_level if granularity_level else "最低级别(仅ItemID)"
            print(f'正在获取过去{days}天内的所有listings，粒度级别: {granularity_desc}，当前页数:', end='')
            
            while True:
                call_data = {
                    'StartTimeFrom': start_time_from.isoformat(),
                    'StartTimeTo': now.isoformat(),
                    'IncludeWatchCount': True,
                    'Pagination': {
                        'EntriesPerPage': 30,  # 建议使用较大的值以提高效率
                        'PageNumber': page_number
                    },
                }
                
                # 只有当granularity_level不为None时才添加GranularityLevel参数
                if granularity_level is not None:
                    call_data['GranularityLevel'] = granularity_level

                response = self.api_trading.execute('GetSellerList', call_data)
                print(f" {page_number}", end='', flush=True)

                if response.reply.Ack not in ['Success', 'Warning']:
                    error_message = ""
                    if hasattr(response.reply, 'Errors') and response.reply.Errors:
                        error_message = response.reply.Errors[0].LongMessage
                    print(f"\nAPI调用失败: {error_message}", file=sys.stderr)
                    break

                item_array = getattr(response.reply, 'ItemArray', None)
                if not (item_array and hasattr(item_array, 'Item')):
                    break
                
                items = item_array.Item
                if not isinstance(items, list):
                    items = [items]

                for item in items:
                    item_dict = self.to_dict_recursive(item)
                    all_listings.append(item_dict)

                if getattr(response.reply, 'HasMoreItems', 'false') == 'false':
                    break
                
                page_number += 1
                
            print(f"\n获取过去{days}天内的所有listings完成，共获取到{len(all_listings)}个商品。")
            return all_listings
            
        except ConnectionError as e:
            print(f"\nAPI 连接或请求出错: {e.response.text if e.response else e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"\n处理GetSellerList时发生未知错误: {e}", file=sys.stderr)
            return []

# 在你的 EbayAPI 类中
    def _upload_pictures(self, picture_paths: list, api_connection) -> dict: # 增加 api_connection 参数
        """
        内部方法：专门负责上传图片。
        返回一个字典，包含成功上传的URL列表和失败的文件列表。
        """
        picture_urls = []
        failed_uploads = []
        
        print(f"准备上传 {len(picture_paths)} 张图片...")
        
        for i, pic_path in enumerate(picture_paths, 1):
            if not os.path.exists(pic_path):
                error_msg = f"图片文件不存在: {pic_path}"
                print(f"❌ {error_msg}", file=sys.stderr)
                failed_uploads.append(error_msg)
                continue
            
            try:
                print(f"  - 正在上传第 {i}/{len(picture_paths)} 张: {os.path.basename(pic_path)}")
                
                with open(pic_path, 'rb') as file:
                    files = {'file': (os.path.basename(pic_path), file)}
                    upload_request = {
                        'PictureName': os.path.basename(pic_path),
                        'PictureSet': 'Supersize',
                        'PictureSystemVersion': 2
                    }
                    
                    # 使用传入的专用连接对象
                    response = api_connection.execute('UploadSiteHostedPictures', upload_request, files=files)
                
                if response.reply.Ack in ['Success', 'Warning']:
                    url = getattr(response.reply, 'SiteHostedPictureDetails', {}).FullURL
                    if url:
                        picture_urls.append(url)
                        print(f"    ✅ 上传成功")
                    else:
                        error_msg = f"图片上传响应中缺少URL: {pic_path}"
                        print(f"    ❌ {error_msg}", file=sys.stderr)
                        failed_uploads.append(error_msg)
                else:
                    error_msg = response.reply.Errors[0].LongMessage if hasattr(response.reply, 'Errors') else '图片上传未知错误'
                    full_error = f"图片上传失败: {error_msg} ({pic_path})"
                    print(f"    ❌ {full_error}", file=sys.stderr)
                    failed_uploads.append(full_error)
                    
            except Exception as e:
                error_msg = f"上传图片时发生异常: {str(e)} ({pic_path})"
                print(f"    ❌ {error_msg}", file=sys.stderr)
                failed_uploads.append(error_msg)

        return {'urls': picture_urls, 'failures': failed_uploads}
    
# 在你的 EbayAPI 类中
# 替换 upload_new_listing_with_pictures 函数
    def upload_new_listing_with_pictures(self, item_dict: dict, picture_paths: list) -> dict:
        """
        上传图片并创建一个新的商品刊登 (终极版 - 强行修正SDK内部状态)。
        """
        if not self.api_trading:
            return {'success': False, 'error': 'Trading API 客户端未初始化'}

        # 1. 上传所有图片
        # (这部分逻辑不变，但为了完整性，我们仍然使用独立的连接对象)
        picture_urls = []
        failed_uploads = []
        if picture_paths:
            try:
                picture_api = Trading(
                    token=self.access_token, config_file=None, appid=self.APP_ID,
                    devid=self.DEV_ID, certid=self.CERT_ID, siteid='0', environment='production'
                )
                upload_result = self._upload_pictures(picture_paths, api_connection=picture_api)
                picture_urls = upload_result['urls']
                failed_uploads = upload_result['failures']
            except Exception as e:
                 return {'success': False, 'error': f"创建图片上传API连接时失败: {e}"}

            if not picture_urls:
                return {'success': False, 'error': f"所有图片均上传失败。详情: {'; '.join(failed_uploads)}"}
            
            print(f"图片上传完成: {len(picture_urls)} 成功, {len(failed_uploads)} 失败。")
            
            import copy
            item_dict_with_pics = copy.deepcopy(item_dict)
            item_dict_with_pics.setdefault('PictureDetails', {})['PictureURL'] = picture_urls
        else:
            item_dict_with_pics = item_dict
            failed_uploads = []

        try:
            print("\n正在为 AddItem 创建专用的API连接...")
            item_api = Trading(
                token=self.access_token, config_file=None, appid=self.APP_ID,
                devid=self.DEV_ID, certid=self.CERT_ID, siteid='0', environment='production'
            )
            
            request_data = {'Item': item_dict_with_pics}
            

            # 强行设置SDK连接对象的内部verb属性，确保它生成正确的XML根节点
            item_api.verb = 'AddItem'
            
            # print("准备上传商品信息...")
            # print(f"  [DEBUG] 调用 API: AddItem")

            # # 再次打印XML以验证修正是否生效
            # print("\n--- [DEBUG] 验证修正后的 AddItem XML 请求 ---")
            # try:
            #     xml_data_to_send = item_api.build_request_data('AddItem', request_data, verb_attrs=None)
            #     print(xml_data_to_send)
            # except Exception as e:
            #     print(f"    [DEBUG] 生成XML时出错: {e}")
            # print("--- [DEBUG] XML 请求结束 ---\n")

            response = item_api.execute('AddItem', request_data)
            response_dict = self.to_dict_recursive(response.reply)

            if response.reply.Ack in ['Success', 'Warning']:
                result = {'success': True, 'ItemID': response_dict.get('ItemID'), 'response': response_dict}
                if failed_uploads:
                    result['warnings'] = f"部分图片上传失败: {'; '.join(failed_uploads)}"
                return result
            else:
                error_msg = response_dict.get('Errors', [{}])[0].get('LongMessage', '未知错误')
                return {'success': False, 'error': error_msg, 'response': response_dict}

        except ConnectionError as e:
            error_msg = f"API 连接或请求出错: {e.response.text if e.response else e}"
            print(error_msg, file=sys.stderr)
            return {'success': False, 'error': str(e)}
        except Exception as e:
            error_msg = f"上传新刊登时发生未知错误: {e}"
            print(error_msg, file=sys.stderr)
            return {'success': False, 'error': str(e)}

    def upload_shipping_tracking_info(self, item_id: str = None, transaction_id: str = None,
                                     order_id: str = None, order_line_item_id: str = None, 
                                     tracking_number: str = None, shipping_carrier: str = None,
                                     shipped_time: datetime = None, is_paid: bool = None, 
                                     is_shipped: bool = None) -> dict:
        """
        上传运单号和发货跟踪信息到eBay，使用CompleteSale API。
        
        参数:
            item_id (str, optional): 商品ID，与transaction_id配对使用
            transaction_id (str, optional): 交易ID，与item_id配对使用  
            order_id (str, optional): 订单ID，用于多行项目订单
            order_line_item_id (str, optional): 订单行项目ID，用于单个行项目
            tracking_number (str, optional): 运单跟踪号
            shipping_carrier (str, optional): 承运商名称（如：UPS, FedEx, USPS等）
            shipped_time (datetime, optional): 发货时间，默认为当前时间
            is_paid (bool, optional): 订单是否已付款
            is_shipped (bool, optional): 订单是否已发货
            
        返回:
            dict: 包含成功状态、错误信息等的结果字典
            
        注意:
            - 必须提供以下标识符之一：
              1. item_id + transaction_id (推荐)
              2. order_line_item_id  
              3. order_id (用于整个订单)
            - tracking_number 和 shipping_carrier 要么都提供，要么都不提供
            - 常用承运商: UPS, FedEx, USPS, DHL, 顺丰速运, 中通快递, 圆通速递, 申通快递, 韵达快递等
        """
        if not self.api_trading:
            print("Trading API 客户端未初始化。", file=sys.stderr)
            return {'success': False, 'error': 'Trading API client not initialized'}
        
        # 验证必需参数 - 必须提供其中一种标识符组合
        has_item_transaction = item_id and transaction_id
        has_order_line_item = order_line_item_id
        has_order_id = order_id
        
        if not (has_item_transaction or has_order_line_item or has_order_id):
            return {
                'success': False, 
                'error': '必须提供以下标识符之一：(item_id + transaction_id) 或 order_line_item_id 或 order_id'
            }
        
        # 验证跟踪号和承运商的相互依赖性
        if (tracking_number and not shipping_carrier) or (shipping_carrier and not tracking_number):
            return {'success': False, 'error': 'tracking_number 和 shipping_carrier 必须同时提供或同时省略'}
        
        try:
            # 构建请求数据
            request_data = {}
            
            # 添加标识符（按优先级：OrderID > OrderLineItemID > ItemID+TransactionID）
            if order_id:
                request_data['OrderID'] = order_id
                identifier_info = f"订单ID={order_id}"
            elif order_line_item_id:
                request_data['OrderLineItemID'] = order_line_item_id
                identifier_info = f"订单行项目ID={order_line_item_id}"
            elif has_item_transaction:
                request_data['ItemID'] = item_id
                request_data['TransactionID'] = transaction_id
                identifier_info = f"商品ID={item_id}, 交易ID={transaction_id}"
            
            # 添加付款状态
            if is_paid is not None:
                request_data['Paid'] = is_paid
            
            # 添加发货状态
            if is_shipped is not None:
                request_data['Shipped'] = is_shipped
            
            # 构建Shipment容器（如果有跟踪信息或发货时间）
            if tracking_number or shipping_carrier or shipped_time:
                shipment_data = {}
                
                # 设置发货时间
                if shipped_time:
                    if not isinstance(shipped_time, datetime):
                        return {'success': False, 'error': 'shipped_time 必须是 datetime 对象'}
                    shipment_data['ShippedTime'] = shipped_time.isoformat()
                
                # 如果提供了跟踪信息，添加ShipmentTrackingDetails
                if tracking_number and shipping_carrier:
                    shipment_data['ShipmentTrackingDetails'] = {
                        'ShipmentTrackingNumber': tracking_number,
                        'ShippingCarrierUsed': shipping_carrier
                    }
                
                if shipment_data:  # 只有在有数据时才添加Shipment容器
                    request_data['Shipment'] = shipment_data
            
            print(f"正在通过CompleteSale上传信息: {identifier_info}")
            if tracking_number and shipping_carrier:
                print(f"跟踪号: {tracking_number}, 承运商: {shipping_carrier}")
            if is_paid is not None:
                print(f"付款状态: {'已付款' if is_paid else '未付款'}")
            if is_shipped is not None:
                print(f"发货状态: {'已发货' if is_shipped else '未发货'}")
            
            # 调用eBay CompleteSale API
            response = self.api_trading.execute('CompleteSale', request_data)

            return response
        except Exception as e:
            error_msg = f"CompleteSale调用时发生未知错误: {e}"
            print(error_msg, file=sys.stderr)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def to_dict_recursive(obj) -> any:
        """
        递归地将 SDK 返回的对象转换为字典。
        支持 dict、list、tuple、带 to_dict 方法或 __dict__ 属性的对象。
        """
        if isinstance(obj, dict):
            return {k: EbayAPI.to_dict_recursive(v) for k, v in obj.items()}
        if hasattr(obj, 'to_dict'):
            return EbayAPI.to_dict_recursive(obj.to_dict())
        if hasattr(obj, '__dict__'):
            return {k: EbayAPI.to_dict_recursive(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        if isinstance(obj, (list, tuple)):
            return [EbayAPI.to_dict_recursive(i) for i in obj]
        return obj