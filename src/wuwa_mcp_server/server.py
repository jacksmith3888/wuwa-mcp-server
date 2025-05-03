import asyncio
import re
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from .api_client import KuroWikiApiClient
from .content_parser import ContentParser, ModuleType
from .markdown_generator import convert_to_markdown

# Initialize FastMCP
mcp = FastMCP("wuwa-mcp-server")

def extract_item_id(html_content: Optional[str]) -> str:
    """
    Extract the item ID of character strategy from HTML content.
    """
    if not html_content:
        return ""

    pattern = r"https://wiki\.kurobbs\.com/mc/item/(\d+)"
    match = re.search(pattern, html_content)
    return match.group(1) if match else ""

async def _get_character_data(character_name: str) -> Dict[str, Any]:
    """
    获取角色数据，包括角色列表、匹配的角色和角色详细信息。

    Args:
        character_name: 要查询的角色的中文名称。

    Returns:
        包含角色详细数据的字典。

    Raises:
        Exception: 获取角色列表失败或找不到角色时引发异常。
    """
    print(f"Fetching data for character: {character_name}")
    async with KuroWikiApiClient() as client:
        # 1. Fetch character list
        characters = await client.fetch_character_list()
        if not characters:
            raise Exception("Failed to fetch character list.")
        print(f"Fetched {len(characters)} characters.")

        # 2. Find matching character
        selected_character = None
        for char in characters:
            if char.get('name', '').lower() == character_name.lower():
                selected_character = char
                break

        if not selected_character:
            raise Exception(f"Character named '{character_name}' not found.")

        entry_id = selected_character.get('content', {}).get('linkId')
        if not entry_id:
            raise Exception(f"Unable to get entry_id for character '{character_name}'.")
        print(f"Found character '{character_name}', entry_id: {entry_id}")

        # 3. Fetch character profile data
        character_raw_data = await client.fetch_entry_detail(entry_id)
        if not character_raw_data:
            raise Exception(f"Failed to fetch profile data for entry_id {entry_id}.")
        return character_raw_data

@mcp.tool()
async def get_artifact_info(artifact_name: str) -> str:
    """获取库街区上的声骸详细信息并以 Markdown 格式返回。

    Args:
        artifact_name: 要查询的声骸套装的中文名称。

    Returns:
        包含声骸信息的 Markdown 字符串，
        或者在找不到声骸或获取数据失败时返回错误消息。
    """
    print(f"收到声骸请求: {artifact_name}")
    async with KuroWikiApiClient() as client:
        try:
            # 1. 获取声骸列表
            artifacts = await client.fetch_artifacts_list()
            if not artifacts:
                return "错误：获取声骸列表失败。"

            # 2. 查找匹配的声骸
            selected_artifact = None
            # 匹配 name 字段
            for artifact in artifacts:
                if artifact.get('name', '').lower() == artifact_name.lower():
                    selected_artifact = artifact
                    break
            if not selected_artifact:
                return f"错误：未找到名为 '{artifact_name}' 的声骸。"

            # 3. 获取 entry_id
            entry_id = selected_artifact.get('content', {}).get('linkId')
            if not entry_id:
                return f"错误：无法获取声骸 '{artifact_name}' 的 entry_id。"

            print(f"找到声骸 '{artifact_name}', entry_id: {entry_id}")

            # 4. 获取声骸详细数据
            print(f"正在获取声骸详细信息，entry_id: {entry_id}...")
            artifact_raw_data = await client.fetch_entry_detail(entry_id)
            if not artifact_raw_data:
                return f"错误：获取 entry_id {entry_id} 的详细数据失败。"

            # 5. 解析声骸内容
            print("正在解析声骸内容...")
            parser = ContentParser()
            # 在线程中运行解析，避免阻塞事件循环
            parsed_artifact_data = await asyncio.to_thread(parser.parse_strategy_content, artifact_raw_data)

            # 6. 生成 Markdown
            print("正在生成 Markdown...")
            artifact_markdown = convert_to_markdown(parsed_artifact_data)

            if not artifact_markdown:
                 print(f"警告：为 {artifact_name} 生成 Markdown 时结果为空。")
                 # 返回一个更友好的消息，而不是错误
                 return f"成功获取 '{artifact_name}' 的数据，但解析后的内容无法生成有效的 Markdown。"

            print(f"成功为 {artifact_name} 生成 Markdown。")
            return artifact_markdown

        except Exception as e:
            print(f"处理 '{artifact_name}' 时发生错误: {str(e)}")
            # import traceback
            # traceback.print_exc() # 用于详细调试
            return f"错误：处理 '{artifact_name}' 时发生意外错误。请检查服务器日志。"

@mcp.tool()
async def get_character_info(character_name: str) -> str:
    """获取库街区上的角色详细信息并以 Markdown 格式返回。

    Args:
        character_name: 要查询的角色的中文名称。

    Returns:
        包含角色信息的 Markdown 字符串，
        或者在找不到角色或获取数据失败时返回错误消息。
    """
    print(f"Received request for character: {character_name}")
    try:
        character_raw_data = await _get_character_data(character_name)

        # 4. Extract strategy_item_id (before parallel parsing)
        strategy_item_id = ""
        for module in character_raw_data["modules"]:
            module_title = module.get("title", "")
            if module_title in {ModuleType.CHARACTER_STRATEGY.value, ModuleType.CHARACTER_STRATEGY_OLD.value}:
                for component in module["components"]:
                    if "content" in component and component["content"]:
                        item_id = extract_item_id(component["content"])
                        if item_id:
                            strategy_item_id = item_id
                            break
            if strategy_item_id:
                break
        print(f"Extracted strategy item ID: {strategy_item_id if strategy_item_id else 'Not found'}")

        # 5. Parallel Processing: Parse profile & Fetch strategy
        parser = ContentParser()
        tasks = []

        # Task 1: Parse main content
        character_profile_task = asyncio.create_task(asyncio.to_thread(parser.parse_main_content, character_raw_data))
        tasks.append(character_profile_task)

        # Task 2: Fetch strategy details if ID exists
        strategy_data_task = None
        if strategy_item_id:
            print("Fetching strategy details...")
            strategy_data_task = asyncio.create_task(KuroWikiApiClient().fetch_entry_detail(strategy_item_id))
            tasks.append(strategy_data_task)

        # Wait for tasks
        await asyncio.gather(*tasks)

        # 6. Process Results
        character_profile_data = character_profile_task.result()

        strategy_raw_data = None
        if strategy_data_task:
            strategy_raw_data = strategy_data_task.result()
            if not strategy_raw_data:
                print(f"Warning: Failed to fetch strategy data for item_id {strategy_item_id}.")
                strategy_raw_data = None

        # 7. Generate Markdown
        character_markdown = convert_to_markdown(character_profile_data)
        strategy_markdown = ""

        if strategy_raw_data:
            print("Parsing strategy content...")
            parsed_strategy_data = parser.parse_strategy_content(strategy_raw_data)
            strategy_markdown = convert_to_markdown(parsed_strategy_data)
            if strategy_markdown:
                print("Strategy content parsed successfully.")
            else:
                print("Warning: Strategy content parsing resulted in empty markdown.")

        # Combine markdown outputs
        combined_markdown = character_markdown
        if strategy_markdown:
            combined_markdown += strategy_markdown

        print(f"Successfully generated markdown for {character_name}.")
        return combined_markdown

    except Exception as e:
        print(f"An error occurred while processing '{character_name}': {str(e)}")
        # import traceback
        # traceback.print_exc() # Uncomment for detailed debugging
        return f"Error: An unexpected error occurred while processing '{character_name}'. Check server logs."

@mcp.tool()
async def get_character_profile(character_name: str) -> str:
    """获取库街区上的角色档案信息并以 Markdown 格式返回。

    Args:
        character_name: 要查询的角色的中文名称。

    Returns:
        包含角色档案信息的 Markdown 字符串，
        或者在找不到角色或获取数据失败时返回错误消息。
    """
    print(f"Received request for character profile: {character_name}")
    try:
        character_raw_data = await _get_character_data(character_name)

        # 4. Parse character profile content
        parser = ContentParser()
        character_profile_data = await asyncio.to_thread(parser.parse_character_profile, character_raw_data)

        # 5. Generate Markdown
        character_markdown = convert_to_markdown(character_profile_data)

        if not character_markdown:
            print(f"Warning: Generated Markdown for {character_name} profile is empty.")
            return f"成功获取 '{character_name}' 的档案数据，但解析后的内容无法生成有效的 Markdown。"
        return character_markdown

    except Exception as e:
        print(f"An error occurred while processing profile for '{character_name}': {str(e)}")
        # import traceback
        # traceback.print_exc() # Uncomment for detailed debugging
        return f"Error: An unexpected error occurred while processing profile for '{character_name}'. Check server logs."

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
