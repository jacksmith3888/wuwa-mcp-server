def convert_to_markdown(parsed_data):
    """
    Convert parsed data to Markdown format.
    Args:
        parsed_data (dict): Parsed structured data.
    Returns:
        str: Markdown formatted string.
    """
    markdown_lines = []
    
    # Add title
    title = parsed_data.get("title", "Unnamed Character")
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")
    
    # Process module data
    modules = parsed_data.get("modules", {})
    for module_title, module_data in modules.items():
        markdown_lines.append(f"## {module_title}")
        markdown_lines.append("")
        
        components = module_data.get("components", [])
        processed_titles = set()  # Used for deduplication
        
        for component in components:
            comp_title = component.get("title", "Unnamed Component")
            if comp_title in processed_titles:
                continue  # Skip already processed titles
            processed_titles.add(comp_title)
            
            markdown_lines.append(f"### {comp_title}")
            markdown_lines.append("")

            # Handle CHARACTER_DATA specific structure
            if "subtitle" in component["data"] and "info_texts" in component["data"]:
                subtitle = component["data"].get("subtitle", "")
                title = component["data"].get("title", "")
                if subtitle:
                    markdown_lines.append(f"- name: **{subtitle}**")
                    markdown_lines.append("")
                info_texts = component["data"].get("info_texts", [])
                if info_texts:
                    for text in info_texts:
                        markdown_lines.append(f"- {text}")
                    markdown_lines.append("")
            
            # Process tabs in skill introduction
            elif "tabs" in component["data"]:
                for tab in component["data"]["tabs"]:
                    tab_title = tab.get("title", "Unnamed Tab")
                    markdown_lines.append(f"#### {tab_title}")
                    markdown_lines.append("")
                    
                    parsed_content = tab.get("parsed_content", {})
                    # Add Markdown content
                    markdown_content = parsed_content.get("markdown_content", "")
                    if markdown_content:
                        markdown_lines.append(markdown_content)
                    else:
                        markdown_lines.append("*(No Content)*")
                    markdown_lines.append("")
                    
                    # Add tables
                    for table in parsed_content.get("tables", []):
                        if not table:
                            continue
                        headers = table[0]
                        markdown_lines.append("| " + " | ".join(headers) + " |")
                        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        for row in table[1:]:
                            markdown_lines.append("| " + " | ".join(row) + " |")
                        markdown_lines.append("")
            
            # Process other components (e.g., skill data, resonance chain, character strategy)
            elif "parsed_content" in component["data"]:
                parsed_content = component["data"]["parsed_content"]
                # For "Resonance Chain" section, prioritize tables data to avoid duplication
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
                        # If no table data, fall back to markdown_content
                        markdown_content = parsed_content.get("markdown_content", "")
                        if markdown_content:
                            markdown_lines.append(markdown_content)
                        else:
                            markdown_lines.append("*(No Content)*")
                else:
                    # Other components output markdown_content and tables normally
                    markdown_content = parsed_content.get("markdown_content", "")
                    if markdown_content:
                        markdown_lines.append(markdown_content)
                    else:
                        markdown_lines.append("*(No Content)*")
                    markdown_lines.append("")
                    
                    # Add tables
                    for table in parsed_content.get("tables", []):
                        if not table:
                            continue
                        headers = table[0]
                        markdown_lines.append("| " + " | ".join(headers) + " |")
                        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        for row in table[1:]:
                            markdown_lines.append("| " + " | ".join(row) + " |")
                        markdown_lines.append("")
    
    # Add character strategy item ID
    strategy_item_id = parsed_data.get("strategy_item_id", "")
    if strategy_item_id:
        markdown_lines.append("## Character Strategy Link")
        markdown_lines.append(f"- Strategy Item ID: {strategy_item_id}")
        markdown_lines.append(f"- Link: [View Strategy](https://wiki.kurobbs.com/mc/item/{strategy_item_id})")
    
    return "\n".join(markdown_lines)
