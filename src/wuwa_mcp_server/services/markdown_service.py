"""Markdown service for converting parsed data to markdown format."""

from typing import Any

from ..core.interfaces import MarkdownServiceProtocol
from ..core.logging_config import LoggerMixin


class MarkdownService(MarkdownServiceProtocol, LoggerMixin):
    """Service for generating markdown from parsed data."""

    def __init__(self):
        """Initialize markdown service."""
        pass

    def generate_character_markdown(self, parsed_data: dict[str, Any], include_strategy: bool = True) -> str:
        """Generate markdown for character data.

        Args:
            parsed_data: Parsed character data.
            include_strategy: Whether to include strategy link.

        Returns:
            Markdown formatted character information.
        """
        try:
            self.logger.info("Generating character markdown")

            markdown_lines = []

            # タイトルを追加
            title = parsed_data.get("title", "Unnamed Character")
            markdown_lines.append(f"# {title}")
            markdown_lines.append("")

            # モジュールデータを処理
            modules = parsed_data.get("modules", {})
            for module_title, module_data in modules.items():
                markdown_lines.extend(self._process_module(module_title, module_data))

            # キャラクター戦略リンクを追加
            if include_strategy:
                strategy_item_id = parsed_data.get("strategy_item_id", "")
                if strategy_item_id:
                    markdown_lines.extend(self._generate_strategy_link_section(strategy_item_id))

            result = "\n".join(markdown_lines)
            self.logger.debug(f"Generated character markdown: {len(result)} characters")
            return result

        except Exception as e:
            self.logger.error(f"Failed to generate character markdown: {e}")
            return f"エラー: マークダウンの生成に失敗しました: {e}"

    def generate_artifact_markdown(self, parsed_data: dict[str, Any]) -> str:
        """Generate markdown for artifact data.

        Args:
            parsed_data: Parsed artifact data.

        Returns:
            Markdown formatted artifact information.
        """
        try:
            self.logger.info("Generating artifact markdown")

            markdown_lines = []

            # タイトルを追加
            title = parsed_data.get("title", "Unnamed Artifact")
            markdown_lines.append(f"# {title}")
            markdown_lines.append("")

            # モジュールデータを処理
            modules = parsed_data.get("modules", {})
            for module_title, module_data in modules.items():
                markdown_lines.extend(self._process_module(module_title, module_data))

            result = "\n".join(markdown_lines)
            self.logger.debug(f"Generated artifact markdown: {len(result)} characters")
            return result

        except Exception as e:
            self.logger.error(f"Failed to generate artifact markdown: {e}")
            return f"エラー: 声骸マークダウンの生成に失敗しました: {e}"

    def generate_strategy_markdown(self, parsed_data: dict[str, Any]) -> str:
        """Generate markdown for strategy data.

        Args:
            parsed_data: Parsed strategy data.

        Returns:
            Markdown formatted strategy information.
        """
        try:
            self.logger.info("Generating strategy markdown")

            markdown_lines = []

            # 戦略セクションのタイトル
            markdown_lines.append("## Character Strategy")
            markdown_lines.append("")

            # モジュールデータを処理
            modules = parsed_data.get("modules", {})
            for module_title, module_data in modules.items():
                # 戦略データの場合はH3レベルから開始
                markdown_lines.extend(self._process_module(module_title, module_data, base_level=3))

            result = "\n".join(markdown_lines)
            self.logger.debug(f"Generated strategy markdown: {len(result)} characters")
            return result

        except Exception as e:
            self.logger.error(f"Failed to generate strategy markdown: {e}")
            return f"エラー: 戦略マークダウンの生成に失敗しました: {e}"

    def _process_module(self, module_title: str, module_data: dict[str, Any], base_level: int = 2) -> list[str]:
        """Process a single module into markdown lines.

        Args:
            module_title: Title of the module.
            module_data: Module data.
            base_level: Base header level for this module.

        Returns:
            List of markdown lines.
        """
        lines = []

        # モジュールタイトル
        header_prefix = "#" * base_level
        lines.append(f"{header_prefix} {module_title}")
        lines.append("")

        # コンポーネントの処理
        components = module_data.get("components", [])
        processed_titles: set[str] = set()  # 重複排除のため

        for component in components:
            comp_title = component.get("title", "Unnamed Component")
            if comp_title in processed_titles:
                continue  # 既に処理済みのタイトルをスキップ
            processed_titles.add(comp_title)

            lines.extend(self._process_component(component, base_level + 1))

        return lines

    def _process_component(self, component: dict[str, Any], header_level: int) -> list[str]:
        """Process a single component into markdown lines.

        Args:
            component: Component data.
            header_level: Header level for this component.

        Returns:
            List of markdown lines.
        """
        lines = []
        comp_title = component.get("title", "Unnamed Component")
        component_data = component.get("data", {})

        # コンポーネントタイトル
        header_prefix = "#" * header_level
        lines.append(f"{header_prefix} {comp_title}")
        lines.append("")

        # CHARACTER_DATA特有の構造を処理
        if "subtitle" in component_data and "info_texts" in component_data:
            lines.extend(self._process_character_data_component(component_data))
        # タブを含むコンポーネントの処理（スキル紹介など）
        elif "tabs" in component_data:
            lines.extend(self._process_tabbed_component(component_data, header_level + 1))
        # その他のコンポーネント（スキルデータ、共鳴チェーン、キャラクター戦略など）
        elif "parsed_content" in component_data:
            lines.extend(self._process_parsed_content_component(component_data, comp_title))

        return lines

    def _process_character_data_component(self, component_data: dict[str, Any]) -> list[str]:
        """Process CHARACTER_DATA specific component structure.

        Args:
            component_data: Component data with CHARACTER_DATA structure.

        Returns:
            List of markdown lines.
        """
        lines = []

        subtitle = component_data.get("subtitle", "")
        if subtitle:
            lines.append(f"- name: **{subtitle}**")
            lines.append("")

        info_texts = component_data.get("info_texts", [])
        if info_texts:
            for text in info_texts:
                lines.append(f"- {text}")
            lines.append("")

        return lines

    def _process_tabbed_component(self, component_data: dict[str, Any], tab_header_level: int) -> list[str]:
        """Process component with tabs (skill introduction).

        Args:
            component_data: Component data with tabs.
            tab_header_level: Header level for tabs.

        Returns:
            List of markdown lines.
        """
        lines = []

        for tab in component_data["tabs"]:
            tab_title = tab.get("title", "Unnamed Tab")
            tab_header_prefix = "#" * tab_header_level
            lines.append(f"{tab_header_prefix} {tab_title}")
            lines.append("")

            parsed_content = tab.get("parsed_content", {})
            lines.extend(self._process_parsed_content(parsed_content))

        return lines

    def _process_parsed_content_component(self, component_data: dict[str, Any], comp_title: str) -> list[str]:
        """Process component with parsed_content.

        Args:
            component_data: Component data.
            comp_title: Component title for special handling.

        Returns:
            List of markdown lines.
        """
        lines = []
        parsed_content = component_data["parsed_content"]

        # 「共鳴チェーン」セクションの場合、重複を避けるためテーブルデータを優先
        if comp_title == "共鸣链":
            tables = parsed_content.get("tables", [])
            if tables:
                lines.extend(self._process_tables(tables))
            else:
                # テーブルデータがない場合はmarkdown_contentにフォールバック
                markdown_content = parsed_content.get("markdown_content", "")
                if markdown_content:
                    lines.append(markdown_content)
                else:
                    lines.append("*(No Content)*")
                lines.append("")
        else:
            # その他のコンポーネントは通常通りmarkdown_contentとテーブルを出力
            lines.extend(self._process_parsed_content(parsed_content))

        return lines

    def _process_parsed_content(self, parsed_content: dict[str, Any]) -> list[str]:
        """Process parsed content with markdown and tables.

        Args:
            parsed_content: Parsed content data.

        Returns:
            List of markdown lines.
        """
        lines = []

        # マークダウンコンテンツを追加
        markdown_content = parsed_content.get("markdown_content", "")
        if markdown_content:
            lines.append(markdown_content)
        else:
            lines.append("*(No Content)*")
        lines.append("")

        # テーブルを追加
        tables = parsed_content.get("tables", [])
        lines.extend(self._process_tables(tables))

        return lines

    def _process_tables(self, tables: list[list[list[str]]]) -> list[str]:
        """Process tables into markdown format.

        Args:
            tables: List of table data.

        Returns:
            List of markdown lines.
        """
        lines = []

        for table in tables:
            if not table:
                continue

            headers = table[0]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in table[1:]:
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")

        return lines

    def _generate_strategy_link_section(self, strategy_item_id: str) -> list[str]:
        """Generate strategy link section.

        Args:
            strategy_item_id: Strategy item ID.

        Returns:
            List of markdown lines.
        """
        lines = [
            "## Character Strategy Link",
            f"- Strategy Item ID: {strategy_item_id}",
            f"- Link: [View Strategy](https://wiki.kurobbs.com/mc/item/{strategy_item_id})",
            "",
        ]
        return lines


# Factory function for dependency injection
def create_markdown_service() -> MarkdownService:
    """Create markdown service.

    Returns:
        MarkdownService instance.
    """
    return MarkdownService()
