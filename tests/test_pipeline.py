import os
import sys
import pytest
import sqlite3

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
from extractor import MockLocalExtractor, SkillExtractorInterface
from pipeline import run_pipeline

TEST_DB = "data/test_resume_skills.db"

@pytest.fixture
def clean_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    database.init_db(TEST_DB)
    yield TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_crud(clean_db):
    """Test 1: Verify database tables creation, save and retrieval."""
    filename = "test_candidate.txt"
    content = "Experienced software engineer with Python and Docker skills."
    skills = ["Python", "Docker"]

    resume_id = database.save_resume_and_skills(filename, content, skills, db_path=clean_db)
    assert resume_id > 0

    record = database.get_resume_skills(filename, db_path=clean_db)
    assert record is not None
    assert record["filename"] == filename
    assert set(record["skills"]) == {"Python", "Docker"}

def test_extractor_boundary_and_case_matching():
    """Test 2: Verify extractor boundary logic avoids false positives like 'Java' in 'JavaScript'."""
    extractor = MockLocalExtractor()
    sample = "I love writing javascript and pYtHoN. I do not know java."
    extracted = extractor.extract_skills(sample)

    assert "Python" in extracted
    assert "JavaScript" in extracted

    # Test pure substring without word match
    substring_only = "This text has javascript only."
    extracted_sub = extractor.extract_skills(substring_only)
    assert "JavaScript" in extracted_sub
    assert "Java" not in extracted_sub

def test_extractor_edge_cases():
    """Test 3: Verify extractor behavior on empty input and non-technical terms."""
    extractor = MockLocalExtractor()

    assert extractor.extract_skills("") == []
    assert extractor.extract_skills("   \n\t  ") == []
    assert extractor.extract_skills("Cooking, baking, carpentry, gardening.") == []

def test_end_to_end_pipeline(clean_db, tmp_path):
    """Test 4: Verify end-to-end pipeline run from directory ingestion to database storage."""
    # Create temporary resume files
    test_dir = tmp_path / "sample_resumes"
    test_dir.mkdir()

    r1 = test_dir / "res1.txt"
    r1.write_text("Backend dev skilled in Python, Django, and MySQL.")

    r2 = test_dir / "res2.txt"
    r2.write_text("Machine learning engineer with PyTorch and Git.")

    results = run_pipeline(data_dir=str(test_dir), db_path=clean_db)

    assert "res1.txt" in results
    assert "res2.txt" in results
    assert set(results["res1.txt"]) == {"Django", "MySQL", "Python"}
    assert set(results["res2.txt"]) == {"Git", "PyTorch", "Machine Learning"}

    all_db_records = database.get_all_resumes_with_skills(db_path=clean_db)
    assert len(all_db_records) == 2
