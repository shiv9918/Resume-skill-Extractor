"""
Edge-Case & Failure Mode Demonstration
-------------------------------------
Demonstrates pipeline robustness against:
1. Empty / whitespace-only resume content (gracefully returns empty skill set).
2. Resumes containing zero controlled technical skills (e.g. non-tech profiles).
3. Substring collision scenarios (e.g., ensuring 'JavaScript' does not falsely trigger 'Java').
4. Database deduplication / idempotent ingestion (safe duplicate runs).
"""

import os
from extractor import MockLocalExtractor
import database

def run_demonstration():
    print("=" * 65)
    print("DEMONSTRATION: EDGE-CASE AND FAILURE RESILIENCE")
    print("=" * 65)

    extractor = MockLocalExtractor()

    # Case 1: Empty text / Null string
    print("\n[Case 1] Empty Text Input:")
    empty_result = extractor.extract_skills("")
    whitespace_result = extractor.extract_skills("   \n\t  ")
    print(f" -> Empty string extracted: {empty_result} (Expected: [])")
    print(f" -> Whitespace string extracted: {whitespace_result} (Expected: [])")
    assert empty_result == [] and whitespace_result == [], "Failed empty text test!"
    print(" [PASSED] Handled gracefully without crash.")

    # Case 2: Resume with only non-controlled skills
    print("\n[Case 2] Non-technical resume with unlisted skills (e.g., Photoshop, Figma):")
    non_tech_text = "Proficient in Adobe Illustrator, Photoshop, Figma, Copywriting, Public Relations."
    non_tech_skills = extractor.extract_skills(non_tech_text)
    print(f" -> Input Text: '{non_tech_text}'")
    print(f" -> Extracted Skills: {non_tech_skills} (Expected: [])")
    assert non_tech_skills == [], "Failed non-technical skills test!"
    print(" [PASSED] Ignored unlisted tools and correctly returned empty list.")

    # Case 3: Substring collision checks
    print("\n[Case 3] Substring Collision & Boundary Isolation:")
    collision_text = "Worked with JavaScript and CSS3 styles."
    collision_skills = extractor.extract_skills(collision_text)
    print(f" -> Input Text: '{collision_text}'")
    print(f" -> Extracted Skills: {collision_skills}")
    assert "Java" not in collision_skills, "False positive detected: 'Java' matched inside 'JavaScript'!"
    assert "JavaScript" in collision_skills, "Failed to match 'JavaScript'!"
    print(" [PASSED] Isolated boundaries properly; 'JavaScript' extracted without false 'Java'.")

    # Case 4: Database Idempotency / Duplicate File Ingestion
    print("\n[Case 4] Database Duplicate Ingestion (Idempotence):")
    test_db = "data/test_demo.db"
    database.init_db(test_db)
    
    # Ingest once
    database.save_resume_and_skills("duplicate_test.txt", "Python and Docker developer", ["Python", "Docker"], db_path=test_db)
    # Ingest again with updated skills
    database.save_resume_and_skills("duplicate_test.txt", "Updated Python developer", ["Python"], db_path=test_db)
    
    record = database.get_resume_skills("duplicate_test.txt", db_path=test_db)
    print(f" -> Database stored record for duplicate_test.txt: {record['skills']}")
    assert record['skills'] == ["Python"], "Database duplicate handling failed!"
    print(" [PASSED] Database handled re-ingestion cleanly without constraint crashes.")

    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n" + "=" * 65)
    print("ALL EDGE-CASE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_demonstration()
