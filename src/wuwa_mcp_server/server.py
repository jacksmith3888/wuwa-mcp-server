import asyncio
import os
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

@mcp.tool()
async def get_character_info(character_name: str) -> str:
    """Fetch character details and strategy from Kuro Wiki and return as Markdown.

    Args:
        character_name: The name of the character to query.

    Returns:
        A markdown string containing the character's profile and strategy information,
        or an error message if the character is not found or data fetching fails.
    """
    print(f"Received request for character: {character_name}")
    async with KuroWikiApiClient() as client:
        try:
            # 1. Fetch character list
            print("Fetching character list...")
            characters = await client.fetch_character_list()
            if not characters:
                return "Error: Failed to fetch character list."
            print(f"Fetched {len(characters)} characters.")

            # 2. Find matching character
            selected_character = None
            for char in characters:
                if char.get('name', '').lower() == character_name.lower():
                    selected_character = char
                    break

            if not selected_character:
                return f"Error: Character named '{character_name}' not found."

            entry_id = selected_character.get('content', {}).get('linkId')
            if not entry_id:
                return f"Error: Unable to get entry_id for character '{character_name}'."
            print(f"Found character '{character_name}', entry_id: {entry_id}")

            # 3. Fetch character profile data
            print("Fetching character profile data...")
            character_raw_data = await client.fetch_entry_detail(entry_id)
            if not character_raw_data:
                return f"Error: Failed to fetch profile data for entry_id {entry_id}."

            if 'data' not in character_raw_data or not character_raw_data.get('data') or 'content' not in character_raw_data['data']:
                return f"Error: Character profile data structure invalid for entry_id {entry_id}."
            content_data = character_raw_data['data']['content']
            print("Character profile data fetched successfully.")

            # 4. Extract strategy_item_id (before parallel parsing)
            strategy_item_id = ""
            if "modules" in content_data:
                for module in content_data["modules"]:
                    module_title = module.get("title", "")
                    if module_title in {ModuleType.CHARACTER_STRATEGY.value, ModuleType.CHARACTER_STRATEGY_OLD.value}:
                        if "components" in module:
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
            character_profile_task = asyncio.create_task(asyncio.to_thread(parser.parse_main_content, content_data))
            tasks.append(character_profile_task)

            # Task 2: Fetch strategy details if ID exists
            strategy_data_task = None
            if strategy_item_id:
                print("Fetching strategy details...")
                strategy_data_task = asyncio.create_task(client.fetch_entry_detail(strategy_item_id))
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
                elif 'data' not in strategy_raw_data or not strategy_raw_data.get('data') or 'content' not in strategy_raw_data['data']:
                    print(f"Warning: Strategy data structure invalid for item_id {strategy_item_id}.")
                    strategy_raw_data = None

            # 7. Generate Markdown
            character_markdown = convert_to_markdown(character_profile_data)
            strategy_markdown = ""

            if strategy_raw_data:
                print("Parsing strategy content...")
                strategy_content_data = strategy_raw_data['data']['content']
                parsed_strategy_data = parser.parse_strategy_content(strategy_content_data)
                strategy_markdown = convert_to_markdown(parsed_strategy_data)
                if strategy_markdown:
                    print("Strategy content parsed successfully.")
                else:
                    print("Warning: Strategy content parsing resulted in empty markdown.")

            # Combine markdown outputs
            combined_markdown = character_markdown
            if strategy_markdown:
                combined_markdown += "\n\n---\n\n## Character Strategy Details\n\n" + strategy_markdown

            print(f"Successfully generated markdown for {character_name}.")
            return combined_markdown

        except Exception as e:
            print(f"An error occurred while processing '{character_name}': {str(e)}")
            # import traceback
            # traceback.print_exc() # Uncomment for detailed debugging
            return f"Error: An unexpected error occurred while processing '{character_name}'. Check server logs."

if __name__ == "__main__":
    mcp.run(transport='stdio')
