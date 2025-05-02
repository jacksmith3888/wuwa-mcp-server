from enum import Enum
from bs4 import BeautifulSoup, NavigableString, Tag


class ModuleType(Enum):
    CHARACTER_DATA = "基础资料"
    CHARACTER_DEVELOPMENT = "角色养成"
    CHARACTER_STRATEGY = "角色攻略"
    CHARACTER_STRATEGY_OLD = "角色养成推荐"


class ContentParser:
    """
    A class for parsing content data from JSON and HTML formats into structured data.
    """
    def parse_main_content(self, content_data):
        """
        Parse the data of the content field, extracting content of specified modules.
        """
        result = {"title": content_data.get("title", ""), "modules": {}}
        target_modules = {mod.value for mod in ModuleType}

        if "modules" in content_data and content_data["modules"]:
            result["modules"] = self._parse_modules(content_data["modules"], target_modules)

        return result

    def parse_strategy_content(self, content_data):
        """
        Parse the strategy content data, processing all modules without filtering specific types.
        """
        result = {"title": content_data.get("title", ""), "modules": {}}

        if "modules" in content_data and content_data["modules"]:
            result["modules"] = self._parse_modules(content_data["modules"])

        return result

    def _parse_component(self, component):
        """Helper method to parse a single component."""
        component_data = {}
        component_title = component.get("title", "Unnamed Component")

        if "tabs" in component and component["tabs"]:
            component_data["tabs"] = [
                {
                    "title": tab.get("title", "Unnamed Tab"),
                    "parsed_content": self._parse_html_content(tab.get("content", "")),
                }
                for tab in component["tabs"]
            ]
        elif "content" in component and component["content"]:
            component_data["parsed_content"] = self._parse_html_content(component["content"])

        return {"title": component_title, "data": component_data} if component_data else None

    def _parse_modules(self, modules_data, target_modules=None):
        """Helper method to parse modules and their components."""
        parsed_modules = {}
        for module in modules_data:
            module_title = module.get("title", "Unnamed Module")
            if target_modules and module_title not in target_modules:
                continue

            module_data = {"components": []}
            if "components" in module and module["components"]:
                # Special handling for CHARACTER_DATA in parse_main_content context
                if target_modules and module_title == ModuleType.CHARACTER_DATA.value:
                    if module["components"]:
                        first_component = module["components"][0]
                        role_data = first_component.get("role", {})
                        component_data = {
                            "title": role_data.get("title", ""),
                            "subtitle": role_data.get("subtitle", ""),
                            "info_texts": [
                                info.get("text", "") for info in role_data.get("info", []) if info.get("text")
                            ]
                        }
                        module_data["components"].append({"title": role_data.get("title", ""), "data": component_data})
                    # Skip other components for CHARACTER_DATA
                    if module_data["components"]:
                         parsed_modules[module_title] = module_data
                    continue # Move to the next module

                # General component parsing for other modules or parse_strategy_content
                for component in module["components"]:
                    parsed_component = self._parse_component(component)
                    if parsed_component:
                        module_data["components"].append(parsed_component)

            if module_data["components"]:
                parsed_modules[module_title] = module_data
        return parsed_modules

    def _convert_tag_to_markdown(self, tag):
        """
        Recursively converts a BeautifulSoup tag and its children to Markdown.
        """
        if isinstance(tag, NavigableString):
            return str(tag).strip()

        markdown_parts = []
        if tag.name == "p":
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children).strip()
            if content:
                markdown_parts.append(content + "\n\n")
        elif tag.name in {"strong", "b"}:
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children).strip()
            if content:
                markdown_parts.append(f"**{content}**")
        elif tag.name in {"em", "i"}:
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children).strip()
            if content:
                markdown_parts.append(f"*{content}*")
        # elif tag.name == "img":
        #     alt = tag.get("alt", "")
        #     src = tag.get("src", "").strip().strip("`").strip()
        #     if src:
        #         markdown_parts.append(f"![{alt}]({src})")
        elif tag.name == "hr":
            markdown_parts.append("---\n\n")
        elif tag.name == "br":
            markdown_parts.append("\n")
        elif tag.name == "table":
            markdown_parts.append(self._convert_table_to_markdown(tag) + "\n\n")
        elif tag.name == "span":
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children).strip()
            markdown_parts.append(content)
        elif tag.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag.name[1])
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children).strip()
            if content:
                markdown_parts.append(f"{'#' * level} {content}\n\n")
        elif tag.name == "ul":
            for item in tag.find_all("li", recursive=False):
                item_content = "".join(self._convert_tag_to_markdown(child) for child in item.children).strip()
                if item_content:
                    markdown_parts.append(f"* {item_content}\n")
            markdown_parts.append("\n")
        elif tag.name == "ol":
            count = 1
            for item in tag.find_all("li", recursive=False):
                item_content = "".join(self._convert_tag_to_markdown(child) for child in item.children).strip()
                if item_content:
                    markdown_parts.append(f"{count}. {item_content}\n")
                    count += 1
            markdown_parts.append("\n")
        elif tag.name == "div":
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children)
            markdown_parts.append(content)
        else:
            # Fallback for unknown tags: process children
            content = "".join(self._convert_tag_to_markdown(child) for child in tag.children)
            markdown_parts.append(content)

        return "".join(markdown_parts)

    def _convert_table_to_markdown(self, table_tag):
        """
        Converts a BeautifulSoup table tag to Markdown table format.
        """
        markdown = ""
        rows = table_tag.find_all("tr")

        if not rows:
            return ""

        header_cells = rows[0].find_all(["th", "td"])
        header_texts = [" ".join(cell.get_text(strip=True).split()) for cell in header_cells]
        markdown += "| " + " | ".join(header_texts) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(header_cells)) + " |\n"

        for row in rows[1:]:
            data_cells = row.find_all("td")
            # Ensure the number of data cells matches the number of header cells
            if len(data_cells) == len(header_cells):
                row_texts = [" ".join(cell.get_text(strip=True).split()) for cell in data_cells]
                markdown += "| " + " | ".join(row_texts) + " |\n"
            # Handle rows with colspan or rowspan if necessary, or simply skip malformed rows
            # For simplicity, this example skips rows that don't match the header count

        return markdown

    def _parse_html_content(self, html_content):
        """
        Parse HTML formatted content, directly converting to Markdown using BeautifulSoup.
        """
        if not html_content:
            return {"markdown_content": "", "tables": []}

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            markdown_output = "".join(self._convert_tag_to_markdown(child) for child in soup.children)
            # Table extraction logic can be added here if needed, currently tables are converted to Markdown
            tables = [] # Placeholder for potential future table data extraction
        except Exception as e:
            print(f"Error parsing HTML with BeautifulSoup: {e}")
            return {"markdown_content": f"<error>Failed to parse HTML: {str(e)}</error>", "tables": []}

        return {"markdown_content": markdown_output.strip(), "tables": tables}
