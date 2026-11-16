import docx
import os

doc = docx.Document(r'S:\Minor project1 report.docx')
out_dir = r'S:\Business\phishing-domain-detection\extracted_images'
os.makedirs(out_dir, exist_ok=True)

# Map relationships to parts
img_parts = {}
for rel_id, rel in doc.part.rels.items():
    if 'image' in rel.target_ref:
        img_parts[rel_id] = (rel.target_ref, rel.target_part)

print(f"Total image rels: {len(img_parts)}")

# Save all images
for rel_id, (target_ref, part) in img_parts.items():
    fname = os.path.basename(target_ref)
    out_path = os.path.join(out_dir, fname)
    with open(out_path, 'wb') as f:
        f.write(part.blob)
    print(f"Saved {fname} ({len(part.blob)} bytes)")

# Find which paragraph has which blip / image
for p_idx, p in enumerate(doc.paragraphs):
    # Check for blip
    xml = p._p.xml
    if 'blip' in xml:
        # find r:embed
        import re
        embeds = re.findall(r'r:embed="([^"]+)"', xml)
        surrounding_text = p.text.strip()
        prev_p = doc.paragraphs[p_idx-1].text.strip() if p_idx > 0 else ""
        next_p = doc.paragraphs[p_idx+1].text.strip() if p_idx < len(doc.paragraphs)-1 else ""
        print(f"\nParagraph {p_idx} has image(s): {embeds}")
        print(f"  Prev: {prev_p[:80]}")
        print(f"  Curr: {surrounding_text[:80]}")
        print(f"  Next: {next_p[:80]}")
