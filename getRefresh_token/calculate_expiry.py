# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone

# --- 在这里输入从 eBay 获取到的时长（秒）---
SECONDS_TO_EXPIRY = 47304000
# ---------------------------------------------

def calculate_iso_expiry_time(seconds_from_now):
    """
    计算从现在开始指定秒数后的UTC时间，并格式化为 eBay 要求的字符串。
    """
    # 获取当前的UTC时间
    current_utc_time = datetime.now(timezone.utc)
    
    # 计算未来的过期时间
    expiry_time = current_utc_time + timedelta(seconds=seconds_from_now)
    
    # 格式化为 ISO 8601 格式，并确保毫秒为三位数，以 'Z' 结尾
    # .isoformat() 会生成类似 '2025-09-14T07:06:14.123456+00:00'
    # 我们需要将其转换为 '2025-09-14T07:06:14.123Z'
    iso_string = expiry_time.isoformat(timespec='milliseconds')
    
    # 将 +00:00 替换为 Z，以完全匹配 eBay 的格式
    formatted_string = iso_string.replace('+00:00', 'Z')
    
    return formatted_string

if __name__ == "__main__":
    if SECONDS_TO_EXPIRY <= 0:
        print("错误：请输入一个正数的秒数。")
    else:
        expiry_string = calculate_iso_expiry_time(SECONDS_TO_EXPIRY)
        print("\n" + "="*50)
        print(f"时长: {SECONDS_TO_EXPIRY} 秒")
        print("计算出的未来过期时间 (UTC, ISO 8601 格式):")
        print(f"\n    {expiry_string}\n")
        print("请将上面这串时间字符串复制到 ebay_rest.json 的")
        print("'refresh_token_expiry' 字段中。")
        print("="*50)