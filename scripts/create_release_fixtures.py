"""Generate only synthetic local acceptance documents, using the bundled document runtime."""
from pathlib import Path
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

root = Path(__file__).resolve().parents[1] / "tmp" / "final-release"
root.mkdir(parents=True, exist_ok=True)
text_path = root / "synthetic-contract.txt"
if not text_path.exists():
    text_path.write_text(
        "SYNTHETIC ACCEPTANCE FIXTURE — no real parties or contract.\n"
        "Section 1. Definitions\nServices means the synthetic work described here.\n"
        "Section 2. Services\nExample Party A shall provide the services.\n"
        "Section 3. Payment\nExample Party B shall pay within thirty days.\n"
        "Section 4. Confidentiality\nEach example party shall protect confidential information.\n"
        "Section 5. Notices\nAll notices must be delivered in writing.\n",
        encoding="utf-8",
    )
text = text_path.read_text(encoding="utf-8-sig")
doc = Document()
styles = getSampleStyleSheet()
story = []
for line in text.splitlines():
    doc.add_paragraph(line)
    story.extend([Paragraph(line, styles["BodyText"]), Spacer(1, 6)])
doc.save(root / "synthetic-contract.docx")
SimpleDocTemplate(str(root / "synthetic-contract.pdf")).build(story)
print("Synthetic TXT/PDF/DOCX fixtures ready")
