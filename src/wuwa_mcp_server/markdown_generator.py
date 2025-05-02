def convert_to_markdown(parsed_data):
    """
    将解析后的数据转换为 Markdown 格式
    参数:
        parsed_data (dict): 解析后的结构化数据
    返回:
        str: Markdown 格式的字符串
    """
    markdown_lines = []
    
    # 添加标题
    title = parsed_data.get("title", "未命名角色")
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")
    
    # 处理模块数据
    modules = parsed_data.get("modules", {})
    for module_title, module_data in modules.items():
        markdown_lines.append(f"## {module_title}")
        markdown_lines.append("")
        
        components = module_data.get("components", [])
        processed_titles = set()  # 用于去重
        
        for component in components:
            comp_title = component.get("title", "未命名组件")
            if comp_title in processed_titles:
                continue  # 跳过已处理的标题
            processed_titles.add(comp_title)
            
            markdown_lines.append(f"### {comp_title}")
            markdown_lines.append("")
            
            # 处理技能介绍中的 tabs
            if "tabs" in component["data"]:
                for tab in component["data"]["tabs"]:
                    tab_title = tab.get("title", "未命名标签")
                    markdown_lines.append(f"#### {tab_title}")
                    markdown_lines.append("")
                    
                    parsed_content = tab.get("parsed_content", {})
                    # 添加 Markdown 内容
                    markdown_content = parsed_content.get("markdown_content", "")
                    if markdown_content:
                        markdown_lines.append(markdown_content)
                    else:
                        markdown_lines.append("*(无内容)*")
                    markdown_lines.append("")
                    
                    # 添加表格
                    for table in parsed_content.get("tables", []):
                        if not table:
                            continue
                        headers = table[0]
                        markdown_lines.append("| " + " | ".join(headers) + " |")
                        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        for row in table[1:]:
                            markdown_lines.append("| " + " | ".join(row) + " |")
                        markdown_lines.append("")
            
            # 处理其他组件（如技能数据、共鸣链、角色攻略）
            elif "parsed_content" in component["data"]:
                parsed_content = component["data"]["parsed_content"]
                # 针对“共鸣链”部分，优先使用 tables 数据，避免重复
                if comp_title == "共鸣链":
                    tables = parsed_content.get("tables", [])
                    if tables:
                        for table in tables:
                            if not table:
                                continue
                            headers = table[0]
                            markdown_lines.append("| " + " | ".join(headers) + " |")
                            markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                            for row in table[1:]:
                                markdown_lines.append("| " + " | ".join(row) + " |")
                            markdown_lines.append("")
                    else:
                        # 如果没有表格数据，则回退到 markdown_content
                        markdown_content = parsed_content.get("markdown_content", "")
                        if markdown_content:
                            markdown_lines.append(markdown_content)
                        else:
                            markdown_lines.append("*(无内容)*")
                else:
                    # 其他组件正常输出 markdown_content 和 tables
                    markdown_content = parsed_content.get("markdown_content", "")
                    if markdown_content:
                        markdown_lines.append(markdown_content)
                    else:
                        markdown_lines.append("*(无内容)*")
                    markdown_lines.append("")
                    
                    # 添加表格
                    for table in parsed_content.get("tables", []):
                        if not table:
                            continue
                        headers = table[0]
                        markdown_lines.append("| " + " | ".join(headers) + " |")
                        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        for row in table[1:]:
                            markdown_lines.append("| " + " | ".join(row) + " |")
                        markdown_lines.append("")
    
    # 添加角色攻略的 item ID
    strategy_item_id = parsed_data.get("strategy_item_id", "")
    if strategy_item_id:
        markdown_lines.append("## 角色攻略链接")
        markdown_lines.append(f"- 攻略 Item ID: {strategy_item_id}")
        markdown_lines.append(f"- 链接: [查看攻略](https://wiki.kurobbs.com/mc/item/{strategy_item_id})")
    
    return "\n".join(markdown_lines)
