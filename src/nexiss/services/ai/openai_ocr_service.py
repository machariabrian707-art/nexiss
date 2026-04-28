from __future__ import annotations

import base64
import httpx
from nexiss.core.config import get_settings
from nexiss.db.models.document import Document
from nexiss.services.ai.types import OCRResult
from nexiss.services.storage import storage_service

settings = get_settings()

class OpenAIOCRService:
    def extract(self, document: Document) -> OCRResult:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for openai OCR")

        # 1. Get file content from storage
        file_bytes = storage_service.get_object_bytes(document.storage_key)
        base64_image = base64.b64encode(file_bytes).decode('utf-8')

        # 2. Call OpenAI Vision
        # Note: GPT-4o handles images. If it's a PDF, this might need conversion 
        # but for a first pass, we'll send it if it's an image.
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_api_key}"
        }

        # Handle different content types
        if document.content_type == "application/pdf":
            # PDFs are tricky for Vision API directly without conversion to images.
            # For now, we'll try to process images. 
            # In a full implementation, we'd use a lib like pdf2image.
            pass

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please perform OCR on this document. Extract all text content accurately. Do not include any commentary or formatting besides newlines."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{document.content_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }

        with httpx.Client(timeout=settings.ocr_timeout_seconds) as client:
            resp = client.post(
                f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers
            )
            resp.raise_for_status()
            result = resp.json()

        text = result['choices'][0]['message']['content']
        
        return OCRResult(
            text=text.strip(),
            page_count=document.page_count or 1
        )
