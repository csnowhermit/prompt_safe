from typing import List, Dict, Any

from app.config import settings
from app.services.input_guard import InputGuardService


class MMGuardService:
    def __init__(self):
        self.input_guard = InputGuardService()
        self.allowed_media_types = {
            "image": ["jpg", "jpeg", "png", "gif", "webp"],
            "audio": ["wav", "mp3", "aac", "ogg"],
            "video": ["mp4", "mov", "avi", "webm"],
            "file": ["pdf", "txt", "docx", "html", "md"]
        }
        self.max_file_sizes = {
            "image": 20 * 1024 * 1024,
            "audio": 50 * 1024 * 1024,
            "video": 200 * 1024 * 1024,
            "file": 50 * 1024 * 1024
        }

    async def process_multimodal_input(self, input_data: Dict[str, Any], user_context: Dict) -> Dict[str, Any]:
        result = {"text_segments": [], "media_segments": []}

        if input_data.get("text"):
            text_result = await self.input_guard.process(
                input_data["text"],
                user_context.get("user_id", ""),
                user_context.get("role", "end_user")
            )
            result["text_segments"].append(text_result)

        for media_item in input_data.get("media", []):
            media_type = media_item.get("type", "")
            file_ext = media_item.get("url", "").split(".")[-1].lower()

            if media_type not in self.allowed_media_types:
                raise ValueError(f"UNSUPPORTED: {media_type}")

            if file_ext not in self.allowed_media_types[media_type]:
                raise ValueError(f"UNSUPPORTED_FORMAT: {file_ext}")

            size = media_item.get("size", 0)
            if size > self.max_file_sizes.get(media_type, 50 * 1024 * 1024):
                raise ValueError("FILE_TOO_LARGE")

            extracted_text = self._extract_text_from_media(media_item)

            text_check = await self.input_guard.process(
                extracted_text,
                user_context.get("user_id", ""),
                user_context.get("role", "end_user")
            )

            result["media_segments"].append({
                "type": media_type,
                "extracted_text": text_check["sanitized_text"],
                "risk_level": text_check["risk_level"]
            })

            if media_type in ["image", "video"]:
                vision_check = self._vision_check(media_item)
                if vision_check.get("is_unsafe", False):
                    raise ValueError(f"UNSAFE_VISUAL: {vision_check.get('category', 'unknown')}")

        return result

    def _extract_text_from_media(self, media_item: Dict) -> str:
        media_type = media_item.get("type", "")
        if media_type == "image":
            return "[OCR提取的图片文本内容]"
        elif media_type == "audio":
            return "[ASR语音转文字内容]"
        elif media_type == "video":
            return "[视频关键帧OCR提取内容]"
        elif media_type == "file":
            return "[文档解析提取的文本内容]"
        return ""

    def _vision_check(self, media_item: Dict) -> Dict:
        return {"is_unsafe": False, "category": None}