
import json
import re
from pypdf import PdfReader

# Configuration
BNSS_PDF = "/Users/nikhilkmenon/Desktop/Law_Lite/a2023-46.pdf"
OUTPUT_FILE = "legal_templates.json"

def extract_bnss_forms(pdf_path):
    """
    Extracts text from the PDF and parses out Forms/Templates defined in the Schedules/Amendments.
    BNSS typically has forms at the end.
    """
    forms = {}
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Regex to find Forms. Usually "FORM No. X" followed by Title
        # Example: FORM No. 1 NOTICE FOR APPEARANCE BY THE POLICE
        
        form_matches = re.finditer(r'(FORM\s+No\.\s*\d+)\s*\n+([A-Z\s\(\)]+)\n+(.*?)(?=(?:FORM\s+No\.\s*\d+)|\Z)', full_text, re.DOTALL | re.MULTILINE)
        
        for match in form_matches:
            form_num = match.group(1).strip() # FORM No. 1
            form_title = match.group(2).strip() # NOTICE FOR ...
            form_body = match.group(3).strip()
            
            # Map BNSS forms to user requests if possible
            # User wants: Legal Notice, Consumer complaint, Rental, Employment, NDA, FIR, Cyber
            
            # BNSS forms are mainly criminal procedure (Summons, Warrants, Bonds)
            # FIR filing steps -> Section 173 of BNSS describes "Information in cognizable cases".
            
            key = f"{form_num}: {form_title}"
            forms[key] = form_body
            
    except Exception as e:
        print(f"Error reading BNSS PDF: {e}")
        
    return full_text, forms

def generate_static_templates():
    """Returns standard templates for items not found in BNSS."""
    return {
        "Legal Notice Format": """[Sender's Name]
[Address]
[Date]

To,
[Recipient's Name]
[Address]

Subject: Legal Notice under Section [Relevant Act] for [Cause of Action]

Sir/Madam,

Under the instructions of my client [Client Name], resident of [Address], I hereby call upon you to note the following:
1. That my client... [Description of relationship/transaction]
2. That... [Description of dispute/grievance]
3. That despite repeated requests... [Failure of recipient]
4. That you are hereby called upon to [Demand: Pay sum/Vacate/etc] within [Days] days of receipt of this notice, failing which my client shall be constrained to initiate legal proceedings against you at your risk and cost.

Copy retained in my office for record.

[Advocate Name]
[Signature]""",
        
        "Consumer Complaint Format": """BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION, [DISTRICT]

Complaint Case No. [Year/Number]

In the matter of:
[Complainant Name]
[Address]     ... Complainant

Versus

[Opposite Party Name/Company]
[Address]     ... Opposite Party

COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019

Respectfully Sheweth:
1. That the complainant is a consumer as defined under the Act...
2. That the complainant purchased/availed service... [Details of transaction]
3. That... [Details of defect/deficiency]
4. That the complainant approached the opposite party... [Correspondence]
5. That the cause of action arose on... [Jurisdiction]
6. Relief Claimed:
   a) Refund of Rs. [Amount]
   b) Compensation for harassment Rs. [Amount]
   c) Litigation costs Rs. [Amount]

[Complainant Signature]
Verification: Verified that contents are true...""",

        "Rental Agreement Checklist": """1. Date and Place of execution.
2. Details of Landlord and Tenant (Name, Father's Name, Address, Aadhaar).
3. Description of the Property (Address, fixtures, fittings).
4. Rent Amount and Due Date.
5. Security Deposit amount and refund conditions.
6. Tenancy Period (Start and End date).
7. Notice Period for termination.
8. Maintenance responsibilities (Minor vs Major repairs).
9. Usage clause (Residential/Commercial).
10. Utility bill payments (Electricity, Water, Maintenance).
11. Rent Increase clause (if renewing).
12. Signatures of both parties and two witnesses.""",

        "Employment Contract Checklist": """1. Job Title and Description.
2. Compensation and Benefits (Salary, PF, Bonus).
3. Employment Type (Full-time/Part-time/Contract).
4. Probation Period.
5. Work Hours and Leave Policy.
6. Termination Clause (Notice period, grounds for dismissal).
7. Confidentiality / Non-Disclosure Agreement (NDA).
8. Non-Compete Clause (if applicable).
9. Intellectual Property Rights (Work for hire).
10. Governing Law and Dispute Resolution.""",

        "NDA Template Structure": """1. PARTIES: Disclosing Party and Receiving Party.
2. DEFINITION OF CONFIDENTIAL INFORMATION: What data is protected.
3. EXCLUSIONS: What is NOT confidential (public domain, prior knowledge).
4. OBLIGATIONS: How to handle the data (No disclosure, limited use).
5. TERM: Duration of the agreement (e.g., 2 years, indefinite).
6. RETURN OF DATA: What happens to data on termination.
7. REMEDIES: Consequences of breach (Injunction, Damages).
8. JURISDICTION: Courts governing the agreement.""",

        "Cyber Complaint Steps": """1. Register at cybercrime.gov.in (National Cyber Crime Reporting Portal).
2. Select Category (Women/Child vs Other Cyber Crimes).
3. Create Login/Submit Anonymously (for certain crimes).
4. Incident Details: Date, Time, Where it happened (Social Media/Email/Website).
5. Suspect Details: If known (Name, Phone, Email).
6. Upload Evidence: Screenshots, Chat logs, URL, Bank Statement.
7. Submit and Note the Acknowledgement Number.
8. Visit nearest Cyber Cell if FIR registration is required by local police."""
    }

def main():
    templates = generate_static_templates()
    
    # Extract FIR filing steps from BNSS PDF (Section 173)
    full_text, bnss_forms = extract_bnss_forms(BNSS_PDF)
    
    # Extract Section 173 text for FIR Steps
    # A simple regex to grab the block if possible, or search for "173. Information in cognizable cases"
    fir_match = re.search(r'173\.\s+Information\s+in\s+cognizable\s+cases\.—(.*?)174\.', full_text, re.DOTALL | re.IGNORECASE)
    if fir_match:
        templates["FIR Filing Steps (BNSS Section 173)"] = fir_match.group(1).strip()
    else:
        # Fallback to general knowledge if extraction is messy
        templates["FIR Filing Steps (General)"] = "1. Visit Police Station having jurisdiction. 2. Give information orally or in writing to Officer-in-Charge. 3. Officer must reduce it to writing (BNSS Sec 173). 4. Informant must sign the report. 5. Receive a free copy of the FIR."

    # Search for specific forms if user asked for "format" map-able to BNSS
    # Notice for appearance -> Form No. 1
    # Summons -> Form No. 2
    
    # If the user asked for "Consumer complaint", BNSS doesn't have it.
    # So we used the static one.
    
    # Consolidate
    final_output = []
    
    for title, content in templates.items():
        final_output.append({
            "Template_Name": title,
            "Content": content
        })
        
    # Append relevant extracted BNSS forms if they match "Legal Notice" broadly
    # Form 1 is "NOTICE FOR APPEARANCE".
    if "FORM No. 1" in bnss_forms: # This key might vary based on regex
        # Finding keys
        for key, val in bnss_forms.items():
            if "NOTICE" in key or "SUMMONS" in key:
                 final_output.append({
                     "Template_Name": f"BNSS {key}",
                     "Content": val
                 })

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
        
    print(f"Templates saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
