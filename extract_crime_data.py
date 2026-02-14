
import csv
import json
import os
import re

# Configuration
INPUT_FILES = [
    "7k  Unique crime articles.csv",
    "Crime_Articles.csv"
]
OUTPUT_FILE = "problem_solution_data.json"

# Keyword Mapping Logic
# This dictionary maps keywords found in the 'content_summary' or 'heading' to the required fields.
KEYWORD_MAP = [
    {
        "keywords": ["salary", "wage", "unpaid", "employer", "employee", "job"],
        "Problem_Type": "Employer unpaid salary/Labour dispute",
        "Applicable_Law": "Payment of Wages Act, 1936 / Industrial Disputes Act, 1947",
        "Relief_Type": "Labour Commissioner Complaint",
        "Average_Timeline": "3-6 months",
        "Escalation": "Labour Court"
    },
    {
        "keywords": ["cheat", "fraud", "scam", "money", "bank", "financial"],
        "Problem_Type": "Financial Fraud / Cheating",
        "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 (Section 318) / IPC Section 420",
        "Relief_Type": "Police Complaint (FIR) / Cyber Crime Portal",
        "Average_Timeline": "6-12 months",
        "Escalation": "Magistrate Court"
    },
    {
        "keywords": ["cyber", "online", "internet", "hack", "data", "phishing"],
        "Problem_Type": "Cyber Crime",
        "Applicable_Law": "Information Technology Act, 2000",
        "Relief_Type": "Cyber Crime Cell Complaint (cybercrime.gov.in)",
        "Average_Timeline": "6-18 months",
        "Escalation": "Adjudicating Officer / High Court"
    },
    {
        "keywords": ["theft", "stolen", "robbery", "burglary", "snatch"],
        "Problem_Type": "Theft / Robbery",
        "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 (Section 303) / IPC Section 378",
        "Relief_Type": "Police Complaint (FIR)",
        "Average_Timeline": "3-9 months",
        "Escalation": "Magistrate Court"
    },
    {
        "keywords": ["assault", "beat", "attack", "violence", "injury", "hurt"],
        "Problem_Type": "Physical Assault",
        "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 (Section 115) / IPC Section 323",
        "Relief_Type": "Police Complaint (FIR) / NC Complaint",
        "Average_Timeline": "6-24 months",
        "Escalation": "Magistrate Court"
    },
    {
        "keywords": ["rape", "sexual", "molestation", "harassment", "woman"],
        "Problem_Type": "Sexual Offences",
        "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 (Section 63/74) / IPC Section 376/354",
        "Relief_Type": "Police Complaint (FIR) - Zero FIR possible",
        "Average_Timeline": "1-3 years (Fast Track Courts)",
        "Escalation": "Sessions Court"
    },
    {
        "keywords": ["murder", "kill", "death", "homicide"],
        "Problem_Type": "Homicide / Murder",
        "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 (Section 103) / IPC Section 302",
        "Relief_Type": "Police Complaint (FIR)",
        "Average_Timeline": "2-5 years",
        "Escalation": "Sessions Court"
    },
    {
        "keywords": ["consumer", "defective", "service", "product", "warranty"],
        "Problem_Type": "Consumer Dispute",
        "Applicable_Law": "Consumer Protection Act, 2019",
        "Relief_Type": "Consumer Forum Complaint",
        "Average_Timeline": "6-12 months",
        "Escalation": "State Commission"
    },
    {
        "keywords": ["rent", "tenant", "landlord", "eviction", "property"],
        "Problem_Type": "Tenancy / Property Dispute",
        "Applicable_Law": "Transfer of Property Act, 1882 / State Rent Control Acts",
        "Relief_Type": "Civil Suit / Rent Controller",
        "Average_Timeline": "1-3 years",
        "Escalation": "District Court"
    },
    {
        "keywords": ["contract", "agreement", "breach"],
        "Problem_Type": "Breach of Contract",
        "Applicable_Law": "Indian Contract Act, 1872",
        "Relief_Type": "Civil Suit for Damages/Specific Performance",
        "Average_Timeline": "1-3 years",
        "Escalation": "District Court"
    }
]

# Default entry
DEFAULT_ENTRY = {
    "Problem_Type": "General Legal Issue",
    "Applicable_Law": "Bharatiya Nyaya Sanhita, 2023 / Relevant Civil Law",
    "Relief_Type": "Consult Legal Practitioner / Police Complaint",
    "Average_Timeline": "Varies",
    "Escalation": "Court of Law"
}

def map_article_to_legal_issue(heading, summary):
    text = (str(heading) + " " + str(summary)).lower()
    
    for mapping in KEYWORD_MAP:
        for keyword in mapping["keywords"]:
            if keyword in text:
                return {
                    "Problem_Type": mapping["Problem_Type"],
                    "Applicable_Law": mapping["Applicable_Law"],
                    "Relief_Type": mapping["Relief_Type"],
                    "Average_Timeline": mapping["Average_Timeline"],
                    "Escalation": mapping["Escalation"],
                    "Source_Heading": heading # Keep reference
                }
    
    # If no specific keyword matches, return None (or default if you want to keep everything)
    # Returning None to filter for "high quality" mapped data as per "extract max" philosophy but meaningful max.
    return None

def main():
    extracted_data = []
    
    for file_name in INPUT_FILES:
        if not os.path.exists(file_name):
            print(f"File not found: {file_name}")
            continue
            
        print(f"Processing {file_name}...")
        try:
            with open(file_name, 'r', encoding='utf-8', errors='replace') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Adjust column names based on actual header inspection
                    # Header: heading,content_summary,article_link,img_link,month,date,time,Year
                    
                    heading = row.get('heading', '').strip()
                    summary = row.get('content_summary', '').strip()
                    
                    if not heading and not summary:
                        continue
                        
                    mapped_entry = map_article_to_legal_issue(heading, summary)
                    if mapped_entry:
                        extracted_data.append(mapped_entry)
                        
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    # Remove duplicates based on heading
    seen_headings = set()
    unique_data = []
    for item in extracted_data:
        if item['Source_Heading'] not in seen_headings:
            seen_headings.add(item['Source_Heading'])
            # Remove the source heading from final output to match exact requested format?
            # User format included: "Problem_Type", "Applicable_Law", "Relief_Type", "Average_Timeline", "Escalation"
            # I will keep Source_Heading out of the final dict to match strict schema, but maybe it's useful context?
            # User request: "from the 7k ... extract and make this into this formate"
            # The example did NOT have source text. So I will clean it.
            
            clean_item = {
                "Problem_Type": item["Problem_Type"],
                "Applicable_Law": item["Applicable_Law"],
                "Relief_Type": item["Relief_Type"],
                "Average_Timeline": item["Average_Timeline"],
                "Escalation": item["Escalation"]
            }
            unique_data.append(clean_item)

    print(f"Extracted {len(unique_data)} mapped issues.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, indent=4, ensure_ascii=False)
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
