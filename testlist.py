from pdfrw import PdfReader

pdf_path = "pdf.net_INITIAL-PACKET-3.pdf"
pdf = PdfReader(pdf_path)

for page_num, page in enumerate(pdf.pages, 1):
    annotations = page.get("/Annots")
    if annotations:
        for annotation in annotations:
            field_type = annotation.get("/FT")
            field_name = annotation.get("/T")
            if field_name:
                print(f"Page {page_num} | Type: {field_type} | Field Name: {field_name[1:-1]}")
