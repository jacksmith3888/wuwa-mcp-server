import httpx
import json

async def fetch_entry_detail(entry_id="1309607355563974656"):
    """
    通过POST请求获取指定entry的详细内容（异步）
    参数:
        entry_id (str): 条目ID
    返回:
        dict: 原始响应数据
    """
    url = "https://api.kurobbs.com/wiki/core/catalogue/item/getEntryDetail"
    
    # 构造form-data格式的请求参数
    form_data = {
        "id": entry_id
    }
    
    # 设置请求头，模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Origin": "https://wiki.kurobbs.com",
        "Referer": "https://wiki.kurobbs.com/",
        "Source": "h5",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Devcode": "IH0A45wV9pzrSfIkkwbCJLKuTvmXhpVE",
        "wiki_type": "9"
    }
    
    try:
        # 使用httpx发送异步POST请求
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=form_data, headers=headers)
            
            # 检查响应状态码
            if response.status_code == 200:
                data = response.json()
                print("请求成功，原始响应数据：")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")  # 仅显示部分响应
                return data
            else:
                print(f"请求失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                return None
    except Exception as e:
        print(f"请求过程中发生错误：{str(e)}")
        return None
