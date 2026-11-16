import docx
import pptx

def inspect_pptx(pptx_path):
    print("="*40)
    print("INSPECTING PPTX:", pptx_path)
    prs = pptx.Presentation(pptx_path)
    print(f"Slide count: {len(prs.slides)}")
    for i, slide in enumerate(prs.slides):
        print(f"\n--- Slide {i+1} (Layout: {slide.slide_layout.name}) ---")
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                print(f"  [Speaker Notes]: {notes}")
        for s in slide.shapes:
            if s.has_text_frame:
                print(f"  [Shape {s.name}]")
                for p in s.text_frame.paragraphs:
                    if p.text.strip():
                        print(f"    - {p.text.strip()}")
            elif s.has_table:
                print(f"  [Table {s.name}]")
                for r_idx, row in enumerate(s.table.rows):
                    row_vals = [c.text.strip().replace('\n', ' ') for c in row.cells]
                    print(f"    Row {r_idx}: {row_vals}")

def inspect_docx(docx_path):
    print("="*40)
    print("INSPECTING DOCX:", docx_path)
    doc = docx.Document(docx_path)
    print(f"Paragraphs count: {len(doc.paragraphs)}")
    print(f"Tables count: {len(doc.tables)}")
    
    # Print headings and title info
    headings = []
    sample_text = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name.startswith('Heading') or p.style.name in ['Title', 'Subtitle']:
            headings.append((p.style.name, t))
        elif len(sample_text) < 50:
            sample_text.append(t)
            
    print("\nHeadings found:")
    for h in headings:
        print(f"  [{h[0]}] {h[1]}")
        
    print("\nFirst 40 non-empty paragraphs:")
    for t in sample_text[:40]:
        print(f"  {t[:120]}")

if __name__ == '__main__':
    inspect_pptx(r'S:\PPT (Final Review).pptx')
    inspect_docx(r'S:\Minor project1 report.docx')
