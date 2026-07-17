import hashlib
from typing import List, Dict, Optional

from app.services.input_guard import InputGuardService


class RAGGuardService:
    def __init__(self):
        self.input_guard = InputGuardService()
        self.allowed_file_types = [".pdf", ".txt", ".md", ".docx", ".html"]
        self.max_file_size = 50 * 1024 * 1024

    async def ingest_document(self, document: Dict, user_context: Dict) -> Dict:
        if not self._verify_source(document.get("source", "")):
            return {"success": False, "reason": "SOURCE_AUTH_FAILED"}

        filetype = document.get("filetype", "")
        if filetype.lower() not in self.allowed_file_types:
            return {"success": False, "reason": "UNSUPPORTED_FILE_TYPE"}

        size = document.get("size", 0)
        if size > self.max_file_size:
            return {"success": False, "reason": "FILE_TOO_LARGE"}

        parsed_text = document.get("content", "")
        guard_result = await self.input_guard.process(parsed_text, user_context.get("user_id", ""),
                                                      user_context.get("role", "end_user"))

        if guard_result["risk_level"] == "red":
            return {"success": False, "reason": "MALICIOUS_CONTENT_DETECTED"}

        content_hash = hashlib.sha256(parsed_text.encode("utf-8")).hexdigest()

        return {
            "success": True,
            "message": "DOCUMENT_INGESTED",
            "content_hash": content_hash,
            "sanitized_text": guard_result["sanitized_text"],
            "risk_level": guard_result["risk_level"]
        }

    def _verify_source(self, source: str) -> bool:
        allowed_sources = ["internal", "trusted_partner", "verified"]
        return source in allowed_sources

    async def filter_retrieval_results(self, raw_results: List[Dict], user_context: Dict) -> List[Dict]:
        filtered = []
        for doc in raw_results:
            if not self._check_acl(doc.get("metadata", {}).get("acl", ""), user_context):
                continue

            if self._contains_malicious_content(doc.get("content", "")):
                continue

            doc["metadata"]["source_label"] = f"[来源: {doc.get('title', '未知文档')}]"
            doc["content"] = doc.get("content", "")[:500]

            filtered.append(doc)

            if len(filtered) >= 5:
                break

        return filtered

    def _check_acl(self, acl: str, user_context: Dict) -> bool:
        user_role = user_context.get("role", "end_user")
        if user_role == "admin":
            return True
        if user_role == "employee" and acl in ["employee", "public"]:
            return True
        if user_role == "end_user" and acl == "public":
            return True
        return False

    def _contains_malicious_content(self, content: str) -> bool:
        malicious_patterns = [
            "ignore all previous", "forget all", "system prompt",
            "API_KEY", "password=", "DROP TABLE"
        ]
        return any(pattern.lower() in content.lower() for pattern in malicious_patterns)