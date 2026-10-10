from abc import ABC, abstractmethod
from typing import List
from skills_list import CONTROLLED_SKILLS

class SkillExtractorInterface(ABC):
    """
    Abstract interface for AI skill extraction.
    Ensures that any model (local, OpenAI, Gemini) adheres to this contract.
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
    A lightweight local 'mock' AI model for demonstration purposes.
    It simulates an AI by performing fuzzy/exact keyword matching 
    against the controlled list of skills. 
    In a real scenario, you can swap this out with a HuggingFace pipeline 
    or OpenAI API call using this same interface.
    """
    def extract_skills(self, resume_text: str) -> List[str]:
        resume_lower = resume_text.lower()
        extracted = []
        for skill in CONTROLLED_SKILLS:
            # Simple keyword matching for the local mock
            if skill.lower() in resume_lower:
                extracted.append(skill)
        return extracted

# Example of how an external AI API would be implemented behind the interface:
# class OpenAIExtractor(SkillExtractorInterface):
#     def __init__(self, api_key):
#         self.api_key = api_key
#     
#     def extract_skills(self, resume_text: str) -> List[str]:
#         # Call OpenAI API here, prompting it to only return skills from CONTROLLED_SKILLS
#         pass
