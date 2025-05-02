import re
from enum import Enum
from bs4 import BeautifulSoup
from readabilipy.simple_json import simple_json_from_html_string
from markdownify import markdownify

# 定义枚举类来维护模块类型
class ModuleType(Enum):
    CHARACTER_DEVELOPMENT = "角色养成"
    CHARACTER_STRATEGY = "角色攻略"

# 定义枚举类来维护角色养成中的子模块
class DevelopmentSubType(Enum):
    SKILL_INTRO = "技能介绍"
    SKILL_DATA = "技能数据"
    RESONANCE_CHAIN = "共鸣链"

def parse_content_data(content_data):
    """
    解析 content 字段的数据，提取指定模块的内容和角色攻略的 item ID
    参数:
        content_data (dict): content 字段的 JSON 数据
    返回:
        dict: 解析后的结构化数据
    """
    result = {
        "title": content_data.get("title", ""),
        "modules": {},
        "strategy_item_id": ""
    }
    
    # 需要处理的模块列表
    target_modules = {mod.value for mod in ModuleType}
    
    # 处理 modules 列表，仅关注目标模块
    if "modules" in content_data and content_data["modules"]:
        for module in content_data["modules"]:
            module_title = module.get("title", "")
            if module_title not in target_modules:
                continue  # 跳过无关模块
            
            module_data = {
                "components": []
            }
            
            # 处理 components 列表
            if "components" in module and module["components"]:
                for component in module["components"]:
                    component_data = {}
                    
                    # 对于“角色养成”，只处理特定子模块
                    if module_title == ModuleType.CHARACTER_DEVELOPMENT.value:
                        component_title = component.get("title", "")
                        
                        # 检查是否有 tabs（如技能介绍），只取 tabs 内容
                        if "tabs" in component and component["tabs"] and component_title == DevelopmentSubType.SKILL_INTRO.value:
                            component_data["tabs"] = []
                            for tab in component["tabs"]:
                                tab_title = tab.get("title", "")
                                tab_content = tab.get("content", "")
                                parsed_tab_content = parse_html_content(tab_content) if tab_content else {}
                                component_data["tabs"].append({
                                    "title": tab_title,
                                    "parsed_content": parsed_tab_content
                                })
                            module_data["components"].append({
                                "title": component_title,
                                "data": component_data
                            })
                        
                        # 检查是否有 content 字段，处理“技能数据”和“共鸣链”
                        elif "content" in component and component["content"] and component_title in {DevelopmentSubType.SKILL_DATA.value, DevelopmentSubType.RESONANCE_CHAIN.value}:
                            component_data["parsed_content"] = parse_html_content(component["content"])
                            module_data["components"].append({
                                "title": component_title,
                                "data": component_data
                            })
                    
                    # 对于“角色攻略”，提取 item ID
                    elif module_title == ModuleType.CHARACTER_STRATEGY.value:
                        if "content" in component and component["content"]:
                            component_data["parsed_content"] = parse_html_content(component["content"])
                            item_id = extract_item_id(component["content"])
                            if item_id:
                                result["strategy_item_id"] = item_id
                            module_data["components"].append({
                                "title": module_title,
                                "data": component_data
                            })
            
            if module_data["components"]:  # 只有当有有效组件时才添加到结果中
                result["modules"][module_title] = module_data
    
    return result

def parse_html_content(html_content):
    """
    解析 HTML 格式的内容，使用 readabilipy 和 markdownify 提取和转换内容
    参数:
        html_content (str): HTML 格式的字符串内容
    返回:
        dict: 解析后的结构化数据，包含 Markdown 格式内容和表格
    """
    if not html_content:
        return {"markdown_content": "", "tables": []}
    
    # 使用 readabilipy 简化 HTML 内容
    try:
        ret = simple_json_from_html_string(html_content, use_readability=True)
        if not ret.get("content"):
            return {"markdown_content": "<error>Page failed to be simplified from HTML</error>", "tables": []}
        
        # 使用 markdownify 将 HTML 转换为 Markdown
        content = markdownify(ret["content"], heading_style="ATX")
    except Exception as e:
        content = f"<error>Failed to convert HTML to Markdown: {str(e)}</error>"
    
    # 使用 BeautifulSoup 提取表格数据（readabilipy 可能不完整保留表格）
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = []
    table_elements = soup.find_all('table')
    for table in table_elements:
        table_data = []
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            table_data.append(row_data)
        tables.append(table_data)
    
    return {"markdown_content": content, "tables": tables}

def extract_item_id(html_content):
    """
    从 HTML 内容中提取角色攻略中的 item ID
    参数:
        html_content (str): HTML 格式的字符串内容
    返回:
        str: 提取的 item ID，如果没有则返回空字符串
    """
    if not html_content:
        return ""
    
    # 攻略ID
    pattern = r"https://wiki\.kurobbs\.com/mc/item/(\d+)"
    match = re.search(pattern, html_content)
    if match:
        return match.group(1)
    return ""
