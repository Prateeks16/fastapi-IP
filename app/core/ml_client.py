import httpx
from typing import List, Dict, Any, Optional

class MLClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate_resume_questions(
        self,
        resume_text: Optional[str] = None,
        resume_url: Optional[str] = None,
        job_description: Optional[str] = None,
        count: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Expected ML service response format:
        [
          {"question_text": "...", "category": "skills", "difficulty": "medium"},
          ...
        ]
        """
        payload = {
            "resume_text": resume_text,
            "resume_url": resume_url,
            "job_description": job_description,
            "count": count,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/resume/generate-questions", json=payload)
            r.raise_for_status()
            return r.json()

    async def evaluate_session(
        self,
        session_id: int,
        answers: List[Dict[str, Any]],
        webhook_url: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Send answers (text/video_url) for scoring.
        ML service will POST results to webhook_url.
        """
        payload = {
            "session_id": session_id,
            "answers": answers,
            "webhook_url": webhook_url,
            "context": context or {},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/evaluate/session", json=payload)
            r.raise_for_status()
            return r.json()
