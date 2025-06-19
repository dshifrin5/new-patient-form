from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName, PdfObject
import os

# === CONFIGURATION ===
pdf_template = "pdf.net_INITIAL-PACKET-3.pdf"
output_pdf = "test_patient_output.pdf"

# === HARD-CODED DATA FOR TESTING ===
test_data = {
  "PT First Name": "John",
  "PT Last Name": "Doe",
  "PT Date Of Birth": "01/01/1990",
  "PT Gender": "other"  # Now it controls all 3 checkboxes properly
}
# === PDF FILL FUNCTION ===
def fill_pdf(input_pdf, output_pdf, data_dict):
  template = PdfReader(input_pdf)
  for page in template.pages:
    annotations = page.get("/Annots")
    if annotations:
      for annotation in annotations:
        if annotation['/Subtype'] == '/Widget' and annotation.get('/T'):
          key = annotation['/T'][1:-1]  # Strip parentheses
          field_type = annotation.get("/FT")

          # === Text fields ===
          if field_type == "/Tx" and key in data_dict:
            value = str(data_dict[key]).strip()
            annotation.update(PdfDict(V=PdfObject(f"({value})"), Ff=1))

          # === Radio Buttons and Checkboxes ===
          elif field_type == "/Btn":
            key_lc = key.lower()
            gender_value = str(data_dict.get("PT Gender", "")).strip().lower()

            # Determine if this button should be selected
            if key_lc == "pt gender male":
              selected = gender_value == "male"
            elif key_lc == "pt gender female":
              selected = gender_value == "female"
            elif key_lc == "pt gender other":
              selected = gender_value == "other"
            else:
              # Generic checkboxes: use the specific key value
              value = str(data_dict.get(key, "")).strip().lower()
              selected = value in ["yes", "true", "1", "checked"]

            # Get the valid export value from /AP dictionary if available
            ap = annotation.get("/AP")
            if ap and "/N" in ap:
              appearances = ap["/N"].keys()
              valid_values = [k for k in appearances if k != "/Off"]
              export_val = valid_values[0] if valid_values else PdfName("Yes")
            else:
              export_val = PdfName("Yes")

            annotation.update(PdfDict(
              V=export_val if selected else PdfName("Off"),
              AS=export_val if selected else PdfName("Off")
            ))



  # Force appearance update so data shows visibly
  if template.Root.AcroForm:
    template.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))
  PdfWriter(output_pdf, trailer=template).write()



# === RUN TEST ===
fill_pdf(pdf_template, output_pdf, test_data)
print(f"✅ Test PDF generated: {output_pdf}")
