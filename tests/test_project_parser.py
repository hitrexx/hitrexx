import os

import docx
import fitz

from app.parser.project_parser import collect_project_content

_CYRILLIC_FONT = os.path.join(
    os.path.dirname(__file__), "..", "app", "exports", "fonts", "DejaVuSans.ttf"
)


def _make_pdf(path: str) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_font(fontname="F0", fontfile=_CYRILLIC_FONT)
    page.insert_text((72, 72), "Проект дома, фундамент 32 м3", fontname="F0")
    document.save(path)
    document.close()


def _make_docx(path: str) -> None:
    document = docx.Document()
    document.add_paragraph("Стены из газобетона, площадь 245 м2")
    document.save(path)


def test_collect_project_content_extracts_text_and_renders_pages(tmp_path):
    pdf_path = str(tmp_path / "project.pdf")
    docx_path = str(tmp_path / "notes.docx")
    _make_pdf(pdf_path)
    _make_docx(docx_path)

    render_dir = str(tmp_path / "renders")
    content = collect_project_content([pdf_path, docx_path], render_dir)

    assert "фундамент 32 м3" in content.text
    assert "газобетона" in content.text
    assert len(content.image_paths) == 1  # one rendered PDF page
    assert content.image_paths[0].endswith(".png")


def test_collect_project_content_passes_through_images(tmp_path):
    image_path = tmp_path / "photo.jpg"
    image_path.write_bytes(b"fake-jpeg-bytes")

    content = collect_project_content([str(image_path)], str(tmp_path / "renders"))

    assert content.image_paths == [str(image_path)]
    assert content.text == ""
