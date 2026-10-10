import os
import glob
from extractor import MockLocalExtractor

def process_resumes(data_dir: str = "sample_data"):
    """
    Pipeline to read sample resumes, pass them to the AI interface,
    and output the structured results.
    """
    extractor = MockLocalExtractor()
    
    results = {}
    search_pattern = os.path.join(data_dir, "*.txt")
    
    for filepath in glob.glob(search_pattern):
        filename = os.path.basename(filepath)
        print(f"Processing {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            resume_text = f.read()
            
        skills = extractor.extract_skills(resume_text)
        results[filename] = skills
        
        print(f"  Extracted Skills: {skills}\n")
        
    return results

if __name__ == "__main__":
    print("Starting Day 2 Pipeline...\n")
    extracted_data = process_resumes()
    print("Pipeline finished successfully.")
