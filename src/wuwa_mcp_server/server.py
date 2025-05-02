import asyncio
import json
import os
from .api_client import fetch_entry_detail, fetch_character_list
from .content_parser import parse_content_data
from .markdown_generator import convert_to_markdown

async def serve():
    """
    主服务函数，负责获取数据、解析内容并生成 Markdown 文件（异步）
    """
    print("开始获取角色列表...")
    try:
        # 获取角色列表
        characters = await fetch_character_list()
        if not characters:
            print("错误：未能获取角色列表，返回为空。")
            return
        
        print(f"获取到 {len(characters)} 个角色。")
        character_name = input("请输入要查询的角色名称：")
        
        # 查找匹配的角色
        selected_character = None
        for char in characters:
            if char.get('name', '').lower() == character_name.lower():
                selected_character = char
                break
        
        if not selected_character:
            print(f"未找到名为 '{character_name}' 的角色。")
            return
        
        entry_id = selected_character.get('content', {}).get('linkId')
        if not entry_id:
            print("错误：无法从选中角色中获取 entry_id。")
            return
        
        print(f"找到角色 '{character_name}'，entry_id: {entry_id}")
        print("开始获取角色数据...")
        
        # 获取数据
        raw_data = await fetch_entry_detail(entry_id)
        if not raw_data:
            print("错误：未能获取数据，返回为空。")
            return
        
        if 'data' not in raw_data or not raw_data['data'] or 'content' not in raw_data['data']:
            print("错误：数据结构不符合预期，无法找到有效的 content 字段。")
            print(f"返回的数据：{json.dumps(raw_data, indent=2, ensure_ascii=False)[:500]}...")
            return
        
        content_data = raw_data['data']['content']
        print("数据获取成功，开始解析内容...")
        
        # 解析内容
        parsed_data = parse_content_data(content_data)
        print("\n解析后的数据：")
        print(json.dumps(parsed_data, indent=2, ensure_ascii=False)[:2000] + "...")  # 限制输出长度以避免过多日志
        print("\n提取的角色攻略 item ID：", parsed_data.get("strategy_item_id", "未找到"))
        
        # 转换为 Markdown 格式
        print("\n开始生成 Markdown 输出...")
        markdown_output = convert_to_markdown(parsed_data)
        print("Markdown 输出（部分）：")
        print(markdown_output[:2000] + "...")  # 仅显示部分 Markdown 输出
        
        # 保存 Markdown 到文件
        output_dir = "output"  # 定义输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # 创建输出目录如果不存在
        
        title = parsed_data.get('title', 'character').replace("/", "_").replace("\\", "_")  # 防止标题中的非法字符
        output_file = os.path.join(output_dir, f"{title}.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        print(f"\nMarkdown 文件已保存为 {output_file}")
    
    except Exception as e:
        print(f"处理过程中发生错误：{str(e)}")
        print("请检查日志或联系开发者以获取更多帮助。")

if __name__ == "__main__":
    asyncio.run(serve())
