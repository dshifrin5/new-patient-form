import pandas as pd
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName, PdfObject
import os

# === CONFIGURATION ===
excel_file = "submissions/submissions.xlsx"
pdf_template = "pdf.net_INITIAL-PACKET-3.pdf"
output_dir = "filled_forms"

# === HARDCODED FIELD MAPPING (Excel column → PDF field name) ===
mapping = {
  "first_name": "PT First Name",
  "last_name": "PT Last Name",
  "middle_initial": "PT Middle Initial",
  "birth_date": "PT Date Of Birth",
  "email": "PT Email",
  "mobile": "PT Mobile Phone Number",
  "home_phone": "PT House Phone Number",
  "call_time": "PT Best Call Time",
  "address1": "PT Address",
  "address2": "PT Address 2",
  "city": "PT City",
  "state": "PT State",
  "zip": "PT ZipCode",
  "emergency_contact": "PT Emergency Contact",
  "gender": "PT Gender",  # Will control Male/Female/Other buttons
  "family_status": "PT Family Status",  # Will control Married/Single/Child/Other
  "relationship": "Relationship Insured",  # Will control Self/Spouse/Child/Other
  "has_secondary": "Secondary Insurance",  # Will control Yes/No
  "responsible_choice": "responsible_choice",  # Just used for logic, not direct fill
  # Will control Spouse/Both/etc
  "parent_last_name": "Responsible Party Last Name",
  "parent_first_name": "Responsible Party First Name",
  "parent_middle_initial": "Responsible Party MI",
  "parent_birth_date": "Responsible Party Birthdate",
  "parent_email": "Responsible Party DOB",
  "physician_name": "Physician Name",
  "pharmacy_info": "Name/Phone Pharmacy",
  "has_secondary": "Secondary Insurance",
  "todays_date": "Todays Date",
  "formCompleterName": "Name of person filing out form",
  "relationshipToPatient": "Response on form relationship",
  "insured_last": "Primary Last Name",
  "insured_first": "Primary First Name",
  "insurance_id": "Primary Insurance ID",
  "insured_birth": "Primary DOB",
  "insured_employer": "Insured Employers Name",
  "plan_name": "Insured Plan Name",
  "allergies": "Allergies",  # Will control Yes/No
  "allergy_details": "Allergies List",
  "serious_illness": "Illness",
  "illness_description": "Illness List",
  "blood_transfusion": "Blood Transfusion",
  "transfusion_date": "Blood Transfusion Date",
  "pregnant": "Pregnant",
  "nursing": "Nursing",
  "birth_control": "Birth Control",
  "anemia": "Anemia",
  "blood_disease": "Blood Disease",
  "development_delay": "Development Delay",
  "fainting": "Fainting",
  "hashimoto_disease": "Hashimoto Disease",
  "heart_murmur": "Heart Murmur",
  "jaundice": "Jaundice",
  "liver_disease": "Liver Disease",
  "pacemaker": "Pacemaker",
  "rheumatism": "Rheumatism",
  "sinus_problems": "Sinus Problems",
  "stroke": "Stroke",
  "ulcers": "Ulcers",
  "arthritis": "Arthritis",
  "cancer": "cancer",
  "diabetes": "Diabetes",
  "genetic_syndrome": "Genetic Syndrome",
  "head_injuries": "Head Injuries",
  "hemophilia": "Hemophilia",
  "joint_conditions": "Joint Conditions",
  "muscular_dystrophy": "Muscular Dystrophy",
  "radiation_treatment": "Radiation Treatment",
  "scarlet_fever": "Scarlet Fever",
  "situs_inversus": "Situs inversus",
  "thyroid_problems": "Thyroid Problems",
  "venereal_disease": "Venereal Disease",
  "artificial_joints": "Artificial Joints",
  "cerebral_palsy": "Cerebral Palsy",
  "ehlers_danlos_syndrome": "Ehlers-Danlos Syndrome",
  "glaucoma": "Glaucoma",
  "heart_conditions": "Heart Conditions",
  "hepatitis": "Hepatitis",
  "kidney_disease": "Kidney Disease",
  "nervous_disorders": "Nervous Disorders",
  "respiratory_problems": "Respiratory Problems",
  "seizure": "Seizure",
  "spina_bifida": "Spina Bifida",
  "tuberculosis": "Tuberculosis",
  "williams_syndrome": "Williams Syndrome",
  "asthma": "Asthma",
  "diflucan": "Diflucan",
  "epilepsy": "Epilepsy",
  "hivaids": "HIV/AIDS",
  "heart_disease": "Heart Disease",
  "high_blood_pressure": "High Blood Pressure",
  "latent_tb": "Latent TB",
  "neutropenia": "Neutropenia",
  "rheumatic_fever": "Rheumatic Fever",
  "shortness_of_breath": "Shortness of Breath",
  "stomachs_problems": "Stomach Problems",
  "tumors": "Tumors",
  "taking_medication": "Medication",
  "medications": "Medications List",
  "allergies": "Allergies",
  "relationshipToPatient": "Filing out form relationship",
  "todays_date": "Response Date"
}

  # Add more mappings here as needed...


df = pd.read_excel(excel_file)
os.makedirs(output_dir, exist_ok=True)

date_fields = [
  "birth_date",
  "parent_birth_date",
  "insured_birth",
  "todays_date",
  "blood_transfusion",
  "parent_birth_date"
]

# === PDF FILL FUNCTION ===
def fill_pdf(input_pdf, output_pdf, data_dict):
  template = PdfReader(input_pdf)
  for page in template.pages:
    annotations = page.get("/Annots")
    if annotations:
      for annotation in annotations:
        if annotation['/Subtype'] == '/Widget' and annotation.get('/T'):
          key = annotation['/T'][1:-1]
          field_type = annotation.get("/FT")
          key_lc = key.lower()

          # === Text Fields ===
          if field_type == "/Tx" and key in data_dict:
            value = str(data_dict[key]).strip()
            annotation.update(PdfDict(V=PdfObject(f"({value})"), Ff=1))
          elif field_type == "/Ch" and key in data_dict:
            value = str(data_dict[key]).strip()
            annotation.update(PdfDict(V=PdfObject(f"({value})")))


          # === Buttons (Checkboxes / Radio Buttons) ===
          elif field_type == "/Btn":
            selected = False

            # Normalize key
            key_lc = key.lower()

            # === GENDER GROUP ===
            gender_val = str(data_dict.get("PT Gender", "")).strip().lower()
            if key_lc == "pt gender male":
              selected = gender_val == "male"
            elif key_lc == "pt gender female":
              selected = gender_val == "female"
            elif key_lc == "pt gender other":
              selected = gender_val == "other"

            # === FAMILY STATUS GROUP ===
            family_status_val = str(data_dict.get("PT Family Status", "")).strip().lower()
            if key_lc == "pt family status married":
              selected = family_status_val == "married"
            elif key_lc == "pt family status single":
              selected = family_status_val == "single"
            elif key_lc == "pt family status child":
              selected = family_status_val == "child"
            elif key_lc == "pt family status other":
              selected = family_status_val == "other"

            # === RELATIONSHIP GROUP ===
            relationship_val = str(data_dict.get("Relationship Insured", "")).strip().lower()
            if key_lc == "relationship insured self":
              selected = relationship_val == "self"
            elif key_lc == "relationship insured spouse":
              selected = relationship_val == "spouse"
            elif key_lc == "relationship insured child":
              selected = relationship_val == "child"
            elif key_lc == "relationship insured other":
              selected = relationship_val == "other"

            # === RESPONSIBLE PARTY CHOICE ===
            responsible_val = str(data_dict.get("responsible_choice", "")).strip().lower()
            if key_lc == "responsible party the person responsible for payment":
              selected = responsible_val == "myself"
            elif key_lc == "responsible niether-not applicable":
              selected = responsible_val == "child"



            # === SECONDARY INSURANCE BUTTONS ===
            secondary_val = str(data_dict.get("Secondary Insurance", "")).strip().lower()
            if key_lc == "secondary insurance yes":
              selected = secondary_val == "yes"
            elif key_lc == "secondary insurance no":
              selected = secondary_val == "no"

            # === SERIOUS ILLNESS BUTTONS ===
            serious_val = str(data_dict.get("Illness", "")).strip().lower()
            if key_lc == "illness yes":
              selected = serious_val == "yes"
            elif key_lc == "illness no":
              selected = serious_val == "no"

            # === BLOOD TRANSFUTION BUTTONS ===
            blood_val = str(data_dict.get("Blood Transfusion", "")).strip().lower()
            if key_lc == "blood transfusion yes":
              selected = blood_val == "yes"
            elif key_lc == "blood transfusion no":
              selected = blood_val == "no"

            # === TAKING MEDICATION BUTTONS ===
            taking_val = str(data_dict.get("Medication", "")).strip().lower()
            if key_lc == "medication yes":
              selected = taking_val == "yes"
            elif key_lc == "medication no":
              selected = taking_val == "no"

            # === ALLERGIES BUTTONS ===
            allergies_val = str(data_dict.get("Allergies", "")).strip().lower()
            if key_lc == "allergies yes":
              selected = allergies_val == "yes"
            elif key_lc == "allergies no":
              selected = allergies_val == "no"

            # === GENERIC CHECKBOX ===
            if not selected:
              if key in data_dict and str(data_dict[key]).strip():
                value = str(data_dict[key]).strip().lower()
                selected = value in ["yes", "true", "1", "checked"]
              else:
                # Skip updating this field if there's no corresponding value
                continue


            # === Determine Export Value ===
            export_val = PdfName("Yes")
            ap = annotation.get("/AP")
            if ap and "/N" in ap:
              normal_appearance = ap["/N"]
              if isinstance(normal_appearance, PdfDict):
                export_vals = [k for k in normal_appearance.keys() if k != PdfName("Off")]
                if export_vals:
                  export_val = export_vals[0]

            annotation.update(PdfDict(
              V=export_val if selected else PdfName("Off"),
              AS=export_val if selected else PdfName("Off")
            ))


  if template.Root.AcroForm:
    template.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject("true")))
  PdfWriter(output_pdf, trailer=template).write()

# === GENERATE A FILLED PDF FOR EACH ROW IN EXCEL ===
for idx, row in df.iterrows():
  data = {}

  # Basic field population
  for excel_field, pdf_field in mapping.items():
    value = row.get(excel_field, "")

    if excel_field in date_fields:
      try:
        # Format as short date like 6/17/25 (use %-m for Linux/macOS)
        value = pd.to_datetime(value).strftime("%#m/%#d/%Y")  # Use "%-m/%-d/%y" on mac
      except:
        pass  # fallback to raw value if parsing fails

    data[pdf_field] = value


  # Gender logic
  gender_val = str(row.get("gender", "")).strip().lower()
  data["PT Gender Male"] = "Yes" if gender_val == "male" else "Off"
  data["PT Gender Female"] = "Yes" if gender_val == "female" else "Off"
  data["PT Gender Other"] = "Yes" if gender_val == "other" else "Off"

  # RESPONSIBLE PARTY logic
  responsible_choice = str(row.get("responsible_choice", "")).strip().lower()
  if responsible_choice == "myself":
    # Check correct box
    data["Responsible Party The person responsible for Payment"] = "Yes"

    # Copy values from patient fields
    data["Responsible Party First Name"] = row.get("first_name", "")
    data["Responsible Party Last Name"] = row.get("last_name", "")
    data["Responsible Party Birthdate"] = row.get("birth_date", "")
    data["Responsible Party DOB"] = row.get("email", "")  # if email is mapped here

  elif responsible_choice == "child":
    # Check "Neither - not applicable"
    data["Responsible Niether-not applicable"] = "Yes"

  output_path = os.path.join(output_dir, f"patient_{idx + 1}.pdf")
  fill_pdf(pdf_template, output_path, data)


print("✅ All PDFs filled! Check the 'filled_forms' folder.")
