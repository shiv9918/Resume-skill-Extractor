import os
import glob
import logging
from typing import Dict, List, Optional
from extractor import SkillExtractorInterface, MockLocalExtractor
import database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_pipeline(
    data_dir: str = "sample_data",
    db_path: str = database.DB_PATH,
    extractor: Optional[SkillExtractorInterface] = None
) -> Dict[str, List[str]]:
    """
    End-to-end pipeline:
    1. Initializes DB.
    2. Ingests all resumes from `data_dir`.
    3. Extracts skills using the configured extractor interface.
    4. Persists the resume content and extracted skills into SQLite.
    5. Returns structured results mapping filename -> list of skills.
    """
    logging.info(f"Initializing database at: {db_path}")
    database.init_db(db_path)

    if extractor is None:
        extractor = MockLocalExtractor()

    results = {}
    search_pattern = os.path.join(data_dir, "*.txt")
    resume_files = sorted(glob.glob(search_pattern))

    if not resume_files:
        logging.warning(f"No resume files found in directory '{data_dir}'.")
        return results

    logging.info(f"Discovered {len(resume_files)} resume file(s) for processing.")

    for filepath in resume_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            extracted_skills = extractor.extract_skills(content)
            database.save_resume_and_skills(filename, content, extracted_skills, db_path=db_path)
            results[filename] = extracted_skills

            logging.info(f"Processed '{filename}' -> Extracted {len(extracted_skills)} skills: {extracted_skills}")
        except Exception as e:
            logging.error(f"Error processing file '{filename}': {e}", exc_info=True)

    logging.info(f"Pipeline finished processing {len(results)} resumes successfully.")
    return results

if __name__ == "__main__":
    print("--- Running Day 3 End-to-End Extraction Pipeline ---")
    extracted_summary = run_pipeline()
    print("\nSummary of Extracted Skills:")
    for resume, skills in extracted_summary.items():
        print(f" - {resume}: {skills}")
