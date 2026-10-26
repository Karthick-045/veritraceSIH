import os
import fitz  # PyMuPDF
from PIL import Image
from sqlalchemy.orm import Session
from app.models.models import Document, DocumentPage, AuditEvent

try:
    import pytesseract
except ImportError:
    pytesseract = None

class ExtractionService:
    @staticmethod
    def extract_document(db: Session, document: Document, user_id: int | None = None) -> list[DocumentPage]:
        file_path = document.file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file {file_path} not found")

        # Clear existing pages if reprocessing
        db.query(DocumentPage).filter(DocumentPage.document_id == document.id).delete()
        db.commit()

        pages_out = []
        doc_dir = os.path.dirname(file_path)

        if document.original_filename.lower().endswith(".pdf"):
            pdf_doc = fitz.open(file_path)
            for page_idx in range(len(pdf_doc)):
                page_num = page_idx + 1
                page = pdf_doc[page_idx]
                rect = page.rect
                page_width = rect.width or 1.0
                page_height = rect.height or 1.0

                # Render page image for Evidence Lens view
                pix = page.get_pixmap(dpi=150)
                image_filename = f"doc_{document.id}_page_{page_num}.png"
                image_path = os.path.join(doc_dir, image_filename)
                pix.save(image_path)

                # Extract words with bounding boxes: (x0, y0, x1, y1, word, block_no, line_no, word_no)
                words = page.get_text("words")
                layout_data = []
                extracted_words = []

                for w in words:
                    x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
                    extracted_words.append(text)
                    # Normalize coordinates to 0.0 - 1.0
                    norm_bbox = {
                        "x0": round(x0 / page_width, 4),
                        "y0": round(y0 / page_height, 4),
                        "x1": round(x1 / page_width, 4),
                        "y1": round(y1 / page_height, 4)
                    }
                    layout_data.append({
                        "text": text,
                        "bbox": norm_bbox,
                        "confidence": 0.98
                    })

                full_text = page.get_text()
                engine = "PyMuPDF"
                confidence = 0.98

                # If PyMuPDF returned almost no text, attempt OCR via Tesseract
                if len(full_text.strip()) < 20 and pytesseract:
                    try:
                        pil_img = Image.open(image_path)
                        ocr_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                        engine = "Tesseract-OCR"
                        img_w, img_h = pil_img.size
                        layout_data = []
                        ocr_words = []
                        total_conf = 0.0
                        conf_count = 0

                        for i in range(len(ocr_data["text"])):
                            t = ocr_data["text"][i].strip()
                            if t:
                                ocr_words.append(t)
                                c = float(ocr_data["conf"][i]) / 100.0 if ocr_data["conf"][i] != "-1" else 0.5
                                total_conf += c
                                conf_count += 1
                                l, top, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                                layout_data.append({
                                    "text": t,
                                    "bbox": {
                                        "x0": round(l / img_w, 4),
                                        "y0": round(top / img_h, 4),
                                        "x1": round((l + w) / img_w, 4),
                                        "y1": round((top + h) / img_h, 4)
                                    },
                                    "confidence": round(c, 2)
                                })
                        full_text = " ".join(ocr_words)
                        confidence = round(total_conf / max(conf_count, 1), 2)
                    except Exception:
                        pass

                doc_page = DocumentPage(
                    document_id=document.id,
                    page_number=page_num,
                    extracted_text=full_text,
                    ocr_engine=engine,
                    mean_confidence=confidence,
                    layout_data=layout_data,
                    image_path=image_path
                )
                db.add(doc_page)
                pages_out.append(doc_page)

            pdf_doc.close()
        else:
            # Direct image file
            try:
                pil_img = Image.open(file_path)
                image_path = file_path
                img_w, img_h = pil_img.size
                engine = "Tesseract-OCR"
                confidence = 0.85
                full_text = ""
                layout_data = []

                if pytesseract:
                    ocr_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                    ocr_words = []
                    total_conf = 0.0
                    conf_count = 0
                    for i in range(len(ocr_data["text"])):
                        t = ocr_data["text"][i].strip()
                        if t:
                            ocr_words.append(t)
                            c = float(ocr_data["conf"][i]) / 100.0 if ocr_data["conf"][i] != "-1" else 0.5
                            total_conf += c
                            conf_count += 1
                            l, top, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                            layout_data.append({
                                "text": t,
                                "bbox": {
                                    "x0": round(l / img_w, 4),
                                    "y0": round(top / img_h, 4),
                                    "x1": round((l + w) / img_w, 4),
                                    "y1": round((top + h) / img_h, 4)
                                },
                                "confidence": round(c, 2)
                            })
                    full_text = " ".join(ocr_words)
                    confidence = round(total_conf / max(conf_count, 1), 2)

                doc_page = DocumentPage(
                    document_id=document.id,
                    page_number=1,
                    extracted_text=full_text,
                    ocr_engine=engine,
                    mean_confidence=confidence,
                    layout_data=layout_data,
                    image_path=image_path
                )
                db.add(doc_page)
                pages_out.append(doc_page)
            except Exception:
                pass

        document.status = "extracted"
        db.commit()

        # Audit event
        audit = AuditEvent(
            case_id=document.case_id,
            user_id=user_id,
            event_type="OCR_EXTRACTED",
            payload={
                "document_id": document.id,
                "pages_count": len(pages_out),
                "engine": pages_out[0].ocr_engine if pages_out else "None",
                "mean_confidence": pages_out[0].mean_confidence if pages_out else 0.0
            }
        )
        db.add(audit)
        db.commit()

        return pages_out
