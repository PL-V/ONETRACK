from pytesseract import pytesseract
from pdf2image import convert_from_path 
import re
import pandas as pd


def extract_text(file):
    images = convert_from_path(file) # pdf to list of images
    # Path to the OCR Model
    path_to_tesseract = r'C:\Users\Imad AHADAD\REVUE_PRESSE\RP_to_text\Ressources\Tesseract-OCR\tesseract.exe'
    pytesseract.tesseract_cmd = path_to_tesseract  # link pytesseract lib with the OCR model

    extracted_text = []
    for image_path in images[0:len(images)]:
        text = pytesseract.image_to_string(image_path)  # Apply OCR 
        extracted_text.append(text)

    return "".join(extracted_text)  # list of strings to one string


def parse_vulnerability_info(text):
    data = []

    # Extracting the title
    title_match = re.search(r'Titre\s+(.*)', text)
    title = title_match.group(1).strip() if title_match else ""

    # Extracting the reference number
    ref_match = re.search(r'Numéro de Référence\s+(\d+)', text)
    reference_number = ref_match.group(1).strip() if ref_match else ""

    # Extracting the publication date
    date_match = re.search(r'Date de Publication\s+(\d+\s\w+\s\d+)', text)
    publication_date = date_match.group(1).strip() if date_match else ""

    # Extracting the risk level
    risk_match = re.search(r'Risque\s+(\w+)', text)
    risk_level = risk_match.group(1).strip() if risk_match else ""

    # Extracting the impacted systems
    systems_match = re.search(r'Systémes affectés\s+([\s\S]+?)(?=\n\s*Direction)', text)
    impacted_systems = systems_match.group(1).strip() if systems_match else ""

    # Extracting external identifiers (CVE)
    cve_match = re.search(r'Identificateurs externes\s+([\s\S]+?)(?=\n\s*Bilan)', text)
    cve_identifiers = cve_match.group(1).strip() if cve_match else ""

    # Extracting the vulnerability summary (Bilan de la vulnérabilité)
    bilan_match = re.search(r'Bilan de la vulnérabilité\s+([\s\S]+?)\n\n', text)
    vulnerability_summary = bilan_match.group(1).strip() if bilan_match else ""

    # Extracting the solution (Solution)
    solution_match = re.search(r'Solution\s+([\s\S]+?)\n\n', text)
    solution = solution_match.group(1).strip() if solution_match else ""

    # # Extracting the risk details (Risque)
    # risque_match = re.search(r'Risque\s+([\s\S]+?)\n\n', text)
    # risks = [line.strip() for line in risque_match.group(1).split('•') if line.strip()] if risque_match else []

    # Prepare data to be stored
    data.append({
        'Title': title,
        'Reference Number': reference_number,
        'Publication Date': publication_date,
        'Risk Level': risk_level,
        'Impacted Systems': impacted_systems,
        'CVE Identifiers': cve_identifiers,
        'Vulnerability Summary': vulnerability_summary,
        'Solution': solution,
        # 'Risks': ', '.join(risks)
    })

    return data

def save_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

text = extract_text(r'C:\Users\Imad AHADAD\Documents\N+ONE DataCenters Intership\test.pdf')
print(text)
vulnerability_info = parse_vulnerability_info(text)
save_to_excel(vulnerability_info, r'C:\Users\Imad AHADAD\Documents\N+ONE DataCenters Intership\vulnerability_report.xlsx')
# print(vulnerability_info)
