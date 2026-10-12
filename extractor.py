from abc import ABC, abstractmethod
import re
from typing import List, Optional
from skills_list import CONTROLLED_SKILLS

class SkillExtractorInterface(ABC):
    """
    Abstract interface for AI skill extraction.
    Ensures that any model (local, OpenAI, Gemini, HuggingFace) adheres to this contract.
    """
    @abstractmethod
    def extract_skills(self, resume_text: str) -> List[str]:
        """
        Takes resume text and returns a list of technical skills 
        extracted from the CONTROLLED_SKILLS list.
        """
        pass

class MockLocalExtractor(SkillExtractorInterface):
    """
    A lightweight local deterministic extractor that adheres to the interface.
    Performs boundary-aware matching against the controlled list of skills,
    preventing false positives (such as matching 'Java' inside 'JavaScript').
    Ideal for clean-room local setup and testing without API credentials.
    """
    def __init__(self, controlled_skills: Optional[List[str]] = None):
        self.skills = controlled_skills or CONTROLLED_SKILLS

    def extract_skills(self, resume_text: str) -> List[str]:
        if not resume_text or not resume_text.strip():
            return []

        extracted = []
        for skill in self.skills:
            # Handle special characters in skills like C++, C#, .NET
            escaped_skill = re.escape(skill)
            # Match on word boundary or punctuation boundary
            pattern = rf'(?<!\w){escaped_skill}(?!\w)'
            if re.search(pattern, resume_text, re.IGNORECASE):
                extracted.append(skill)
        return sorted(list(set(extracted)))

class LLMSkillExtractor(SkillExtractorInterface):
    """
    Template for connecting a cloud/local LLM (e.g. Gemini, OpenAI, Ollama).
    Isolates external API network calls behind the SkillExtractorInterface.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def extract_skills(self, resume_text: str) -> List[str]:
        if not self.api_key:
            # Fall back to local mock if no API key is supplied
            return MockLocalExtractor().extract_skills(resume_text)
        # Placeholder for external LLM API call:
        # prompt = f"Given the text: {resume_text}\nExtract skills matching: {CONTROLLED_SKILLS}"
        # response = call_llm(prompt)
        # return parse_skills(response)
        return MockLocalExtractor().extract_skills(resume_text)
