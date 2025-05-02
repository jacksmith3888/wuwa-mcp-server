import asyncio
import json
import os
from .api_client import KuroWikiApiClient # Import the class
from .content_parser import parse_content_data
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

            # Fetch data
            raw_data = await client.fetch_entry_detail(entry_id) # Use client instance
            if not raw_data:
                print("Error: Failed to fetch data, returned empty.")
                return # Exit serve function if fetch failed

            if 'data' not in raw_data or not raw_data['data'] or 'content' not in raw_data['data']:
                print("Error: Data structure does not match expectations, unable to find valid content field.")
                print(f"Returned data: {json.dumps(raw_data, indent=2, ensure_ascii=False)[:500]}...")
                return # Exit serve function if data structure is wrong

            content_data = raw_data['data']['content']
            print("Data fetched successfully, starting to parse content...")

            # Parse content
            parsed_data = parse_content_data(content_data)
            print("\nParsed data:")
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False)[:2000] + "...")
            print("\nExtracted character strategy item ID:", parsed_data.get("strategy_item_id", "Not found"))

            # Convert to Markdown format
            print("\nStarting to generate Markdown output...")
            markdown_output = convert_to_markdown(parsed_data)
            print("Markdown output (partial):")
            print(markdown_output[:2000] + "...")

            # Save Markdown to file
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            title = parsed_data.get('title', 'character').replace("/", "_").replace("\\", "_")
            output_file = os.path.join(output_dir, f"{title}.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_output)
            print(f"\nMarkdown file saved as {output_file}")

        except Exception as e:
            print(f"An error occurred during processing: {str(e)}")
            print("Please check the logs or contact the developer for further assistance.")
    # End of async with block

# This block is now correctly outside the serve function
if __name__ == "__main__":
    asyncio.run(serve())
