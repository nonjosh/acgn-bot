"""Message helper module."""

import chinese_converter

from helpers.media import MediaHelper
from helpers.media_list_state import MediaListState


class MessageHelper:
    """Message helper class"""

    def _group_media_helpers(self, include_without_checker: bool = True):
        """Group helpers by media type.

        Args:
            include_without_checker (bool): When False, exclude helpers without a checker.

        Returns:
            dict[str, list[MediaHelper]]: Mapping of media type to helpers in original order.
        """
        groups = {"comic": [], "novel": []}
        for helper in MediaListState.media_helper_list:
            if not include_without_checker and not helper.checker:
                continue
            if helper.media_type not in groups:
                groups[helper.media_type] = []
            groups[helper.media_type].append(helper)
        return groups

    def get_update_chapters_html_message(self, media_helper: MediaHelper) -> str:
        """Get update chapters as html message string

        Args:
            media_helper (MediaHelper): media helper object

        Returns:
            str: message content (html)
        """

        # 元尊 comic updated!
        content_html_text = f"{media_helper.media_type} {media_helper.name} updated!\n"

        # qiman59 | cocomanga
        content_html_text += media_helper.get_urls_text()

        # Updated 3 chapter(s): 第六百二十六章 挑戰鐘太丘, 第六百二十七章 虛珠, 第六百二十八章 巔峰對決
        updated_chapter_list = media_helper.checker.updated_chapter_list
        content_html_text += f"Updated {len(updated_chapter_list)} chapter(s): "
        chapter_texts = [
            f"<a href='{updated_chapter.url}'>{updated_chapter.title}</a>"
            for updated_chapter in updated_chapter_list
        ]
        content_html_text += ", ".join(chapter_texts)

        # Convert to traditional Chinese
        return chinese_converter.to_traditional(content_html_text)

    def get_config_list_html_message(self) -> str:
        """Get config list as html message string

        Returns:
            str: html message
        """
        html_response = (
            f"<b>Current Config (total {len(MediaListState.media_helper_list)})</b>\n"
        )

        # Group all helpers (regardless of checker) by media type
        groups = self._group_media_helpers(include_without_checker=True)

        # Render groups in a stable order: comics first, then novels
        for media_type in ("comic", "novel"):
            helpers = groups.get(media_type, [])
            if not helpers:
                continue
            # Group header
            html_response += f"\n<b>{media_type.title()}</b>\n"
            # Items (omit media type on each line since grouped)
            for helper in helpers:
                html_response += f"{helper.name}: " + helper.get_urls_text()

        return html_response

    def get_latest_chapter_list_html_message(self) -> str:
        """Get latest chapters list as html message string

        Returns:
            str: html message
        """
        html_response = (
            f"<b>Latest Chapters (total {len(MediaListState.media_helper_list)})</b>\n"
        )

        # Group helpers by media type (only include those with a checker)
        groups = self._group_media_helpers(include_without_checker=False)

        # Render groups in a stable order: comics first, then novels
        for media_type in ("comic", "novel"):
            helpers = groups.get(media_type, [])
            if not helpers:
                continue
            # Group header
            html_response += f"\n<b>{media_type.title()}</b>\n"
            # Items (omit media type on each line since grouped)
            for helper in helpers:
                latest_chapter = helper.checker.get_latest_chapter()
                if latest_chapter is not None:
                    html_response += (
                        f"<a href='{helper.check_url}'>{helper.name}</a>: "
                        f"<a href='{latest_chapter.url}'>{latest_chapter.title}</a> "
                        f"(total: {len(helper.checker.chapter_list)}ch)\n"
                    )
                else:
                    html_response += (
                        f"<a href='{helper.check_url}'>{helper.name}</a>: N/A\n"
                    )
        return html_response

    def get_last_check_time_list_html_message(self) -> str:
        """Get last check time list as html message string

        Returns:
            str: html message
        """
        html_response = (
            f"<b>Late Check Time (total {len(MediaListState.media_helper_list)})</b>\n"
        )

        # Group helpers by media type (only include those with a checker)
        groups = self._group_media_helpers(include_without_checker=False)

        # Render groups in a stable order: comics first, then novels
        for media_type in ("comic", "novel"):
            helpers = groups.get(media_type, [])
            if not helpers:
                continue
            # Group header
            html_response += f"\n<b>{media_type.title()}</b>\n"
            # Items (omit media type on each line since grouped)
            for helper in helpers:
                html_response += (
                    f"{helper.checker.last_check_time}| "
                    f"<a href='{helper.check_url}'>{helper.name}</a>\n"
                )

        return html_response
