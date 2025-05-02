import asyncio
import json
import os
from .api_client import KuroWikiApiClient # Import the class
from .content_parser import ContentParser
from .markdown_generator import convert_to_markdown

async def serve():
    """
    Main service function to fetch data, parse content, and generate Markdown files (asynchronous).
    """
    print("Starting API client initialization...")
    # Use async with to manage the client lifecycle
    async with KuroWikiApiClient() as client:
        print("Starting to fetch character list...")
        try:
            # Fetch character list
            characters = await client.fetch_character_list() # Use client instance
            if not characters:
                print("Error: Failed to fetch character list, returned empty.")
                return # Exit serve function if no characters

            print(f"Fetched {len(characters)} characters.")
            character_name = input("Please enter the name of the character to query: ")

            # Find matching character
            selected_character = None
            for char in characters:
                if char.get('name', '').lower() == character_name.lower():
                    selected_character = char
                    break

            if not selected_character:
                print(f"Character named '{character_name}' not found.")
                return # Exit serve function if character not found

            entry_id = selected_character.get('content', {}).get('linkId')
            if not entry_id:
                print("Error: Unable to get entry_id from selected character.")
                return # Exit serve function if no linkId

            print(f"Found character '{character_name}', entry_id: {entry_id}")
            print("Starting to fetch character data...")

            # Fetch character profile data
            character_raw_data = await client.fetch_entry_detail(entry_id) # Use client instance
            if not character_raw_data:
                print("Error: Failed to fetch character data, returned empty.")
                return # Exit serve function if fetch failed

            if 'data' not in character_raw_data or not character_raw_data['data'] or 'content' not in character_raw_data['data']:
                print("Error: Character data structure does not match expectations, unable to find valid content field.")
                print(f"Returned character data: {json.dumps(character_raw_data, indent=2, ensure_ascii=False)[:500]}...")
                return # Exit serve function if data structure is wrong

            content_data = character_raw_data['data']['content']
            print("Character data fetched successfully, starting to parse content...")

            # Parse main content using ContentParser
            parser = ContentParser()
            character_profile_data = parser.parse_main_content(content_data)
            strategy_item_id = character_profile_data.get("strategy_item_id")
            print("\nExtracted character strategy item ID:", strategy_item_id if strategy_item_id else "Not found")

            # --- Parallel Processing ---
            tasks = []
            
            # Task 1: Generate markdown for the character profile content
            character_markdown_task = asyncio.create_task(asyncio.to_thread(convert_to_markdown, character_profile_data))
            tasks.append(character_markdown_task)

            # Task 2: Fetch strategy details if ID exists
            strategy_data_task = None
            if strategy_item_id:
                strategy_data_task = asyncio.create_task(client.fetch_entry_detail(strategy_item_id))
                tasks.append(strategy_data_task)

            # Wait for tasks to complete
            await asyncio.gather(*tasks)
            
            # --- Check Strategy Data Immediately ---
            strategy_raw_data = None
            if strategy_data_task:
                strategy_raw_data = strategy_data_task.result()
                if not strategy_raw_data:
                    print("Error: Failed to fetch strategy data, returned empty.")
                    strategy_raw_data = None
                elif 'data' not in strategy_raw_data or not strategy_raw_data['data'] or 'content' not in strategy_raw_data['data']:
                    print("Error: Strategy data structure does not match expectations, unable to find valid content field.")
                    print(f"Returned strategy data: {json.dumps(strategy_raw_data, indent=2, ensure_ascii=False)[:500]}...")
                    strategy_raw_data = None
            
            # --- Combine Results ---
            character_markdown = character_markdown_task.result()
            strategy_markdown = ""

            if strategy_raw_data:
                print("Strategy details fetched successfully, parsing content...")
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
            
            # Save final Markdown to file
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Use the title from the character profile data
            title = character_profile_data.get('title', 'character').replace("/", "_").replace("\\", "_") 
            output_file = os.path.join(output_dir, f"{title}.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(combined_markdown) # Write the combined output
            print(f"\nMarkdown file saved as {output_file}")

        except Exception as e:
            print(f"An error occurred during processing: {str(e)}")
            print("Please check the logs or contact the developer for further assistance.")
    # End of async with block

# This block is now correctly outside the serve function
if __name__ == "__main__":
    asyncio.run(serve())
