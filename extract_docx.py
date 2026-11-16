import docx

doc = docx.Document(r'S:\Minor project1 report.docx')
with open(r'S:\Business\phishing-domain-detection\report_text.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t:
            f.write(f"[{i}] {t}\n")

print(f"Extracted {len(doc.paragraphs)} paragraphs.")
