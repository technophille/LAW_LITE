
import os
import json
import re
from pypdf import PdfReader

# Configuration
PDF_DIR = "/Users/nikhilkmenon/Desktop/Law_Lite"
OUTPUT_FILE = "legal_data.json"

# File mapping to Act Names
FILE_ACT_MAP = {
    "ipc_act.pdf": "Indian Penal Code (IPC)",
    "Bharatiya Nyaya Sanhita (new criminal laws).pdf": "Bharatiya Nyaya Sanhita (BNS)",
    "CP Act 2019_1732700731.pdf": "Consumer Protection Act 2019",
    "it_act_2000_updated.pdf": "Information Technology Act 2000",
    "IC ACT.pdf": "Indian Contract Act 1872",
    "the_companies_act,_2013_no._18_of_2013_date_29.08.2013.pdf": "Companies Act 2013",
    "THE TRANSFER OF PROPERTY ACT, 1882.pdf": "Transfer of Property Act 1882",
    # "property act.pdf" seems duplicate or similar, skipping for now or can process if distinct
    "Labour Laws.pdf": "Labour Laws" # Placeholder if file exists
}

def clean_text(text):
    """Cleans extracted text by removing excessive whitespace and artifacts."""
    if not text:
        return ""
    # Remove header/footer noise (simplistic approach)
    # merged multiline sentences
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_section_data(text, act_name):
    """
    Parses text to identify sections and extract relevant fields.
    Refined for better capture.
    """
    sections_data = []
    
    # Generic regex for Section start. 
    # BNS: "1. (1)", IPC: "Section 302.", Contract: "10."
    # Matches "\n123. " or "Section 123. "
    # We use a lookahead to split by the *next* section start
    
    # Common pattern for start of a section
    section_start_pattern = r'(?:^|\s)(?:Section\s+)?(\d+[A-Za-z]*)\.?\s+(?=[A-Z])'
    
    # Split text by section numbers
    # capturing the delimiter (section number) to keep it
    parts = re.split(section_start_pattern, text)
    
    # parts[0] is intro text key, parts[1] is number, parts[2] is content, parts[3] is number...
    
    if len(parts) < 2:
        # Fallback for simple numbering "1. " at start of line
        parts = re.split(r'(?:^|\s)(\d+)\.\s+(?=[A-Z])', text)

    # If still low, just return empty or try one big block?
    # Let's iterate what we found.
    
    # Processing in pairs of (Number, Content)
    # parts[0] is preamble/before first match
    
    current_sec_num = "Intro"
    
    # We iterate starting from index 1 which should be a number
    for i in range(1, len(parts), 2):
        if i+1 >= len(parts): break
        
        sec_num = parts[i].strip()
        content = parts[i+1].strip()
        
        # Check if content is actually a section or just a reference number
        # A valid section usually has some length
        if len(content) < 5: 
            continue

        # --- Extraction Logic ---
        
        # 1. Applicable Scenario (The main description)
        # Usually the whole text until the Penalty clause
        applicable_scenario = content
        
        # 2. Penalty
        # Search for penalty keywords
        penalty = ""
        # Improved regex for penalty: captures until end of sentence or ;
        penalty_patterns = [
            r'(shall be punished with.*?)(\.|;|$)',
            r'(punishable with.*?)(\.|;|$)',
            r'(imprisonment for.*?)(\.|;|$)',
            r'(fine which may extend.*?)(\.|;|$)'
        ]
        
        for pat in penalty_patterns:
            match = re.search(pat, content, re.IGNORECASE)
            if match:
                penalty_text = match.group(1).strip()
                if len(penalty_text) > len(penalty): # Keep the longest match which likely has more detail
                    penalty = penalty_text

        # 3. Relief
        # Search for relief keywords (compensation, etc)
        relief = ""
        relief_patterns = [
            r'(fail to pay.*?)(?:\.|;|$)', # Often context for relief/consequence
            r'(compensation.*?)(?:\.|;|$)',
            r'(refund.*?)(?:\.|;|$)',
            r'(damages.*?)(?:\.|;|$)',
            r'(restore.*?)(?:\.|;|$)',
            r'(reimburse.*?)(?:\.|;|$)'
        ]
        
        for pat in relief_patterns:
            match = re.search(pat, content, re.IGNORECASE)
            if match:
                relief_text = match.group(1).strip()
                if len(relief_text) > len(relief):
                    relief = relief_text
        
        # Clean scenario to remove the penalty text if it looks redundant? 
        # Sometimes better to leave it for context. User asked for "extract max".
        
        entry = {
            "Act_Name": act_name,
            "Section": sec_num,
            "Applicable_Scenario": applicable_scenario,
            "Penalty": penalty,
            "Relief": relief
        }
        
        sections_data.append(entry)

    return sections_data

def process_pdf(pdf_path, act_name):
    print(f"Processing {pdf_path}...")
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        # Pre-process text to fix line breaks within sentences
        full_text = clean_text(full_text)
        
        return extract_section_data(full_text, act_name)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def main():
    all_data = []
    
    files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    
    for filename in files:
        if filename in FILE_ACT_MAP:
            file_path = os.path.join(PDF_DIR, filename)
            act_name = FILE_ACT_MAP[filename]
            data = process_pdf(file_path, act_name)
            all_data.extend(data)
        else:
            print(f"Skipping unknown file: {filename}")

    # Write to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    
    print(f"Extraction complete. Data saved to {OUTPUT_FILE}")
    print(f"Total entries extracted: {len(all_data)}")

if __name__ == "__main__":
    main()
