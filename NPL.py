from flask import Flask, request, jsonify
import os
import base64
import pandas as pd
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

SAVE_FOLDER = "submissions"
EXCEL_FILE = os.path.join(SAVE_FOLDER, "submissions.xlsx")

os.makedirs(SAVE_FOLDER, exist_ok=True)

# Initialize Excel if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Full Name", "DOB", "Phone", "Email", "Insurance", "Reason for Visit", "Timestamp"])
    df.to_excel(EXCEL_FILE, index=False)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'New Patient Form', ln=True, align='C')
        self.ln(10)

    def add_patient_info(self, data):
        self.set_font('Arial', '', 12)
        for label, value in data.items():
            if label != 'signature':
                self.cell(0, 10, f"{label}: {value}", ln=True)

    def add_signature(self, signature_path):
        self.ln(10)
        self.cell(0, 10, "Signature:", ln=True)
        self.image(signature_path, w=60)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        print("[DEBUG] Received:", data)
        name = data.get("name")
        dob = data.get("dob")
        phone = data.get("phone")
        email = data.get("email")
        insurance = data.get("insurance")
        reason = data.get("reason")
        signature_data = data.get("signature")  # base64
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        # Save signature image
        signature_path = os.path.join(SAVE_FOLDER, f"signature_{timestamp}.png")
        with open(signature_path, "wb") as sig_file:
            sig_file.write(base64.b64decode(signature_data.split(",")[1]))

        # Create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.add_patient_info({
            "Full Name": name,
            "DOB": dob,
            "Phone": phone,
            "Email": email,
            "Insurance": insurance,
            "Reason for Visit": reason,
            "Timestamp": timestamp
        })
        pdf.add_signature(signature_path)
        pdf_path = os.path.join(SAVE_FOLDER, f"form_{timestamp}.pdf")
        pdf.output(pdf_path)

        # Append to Excel
        df = pd.read_excel(EXCEL_FILE)
        df.loc[len(df)] = [name, dob, phone, email, insurance, reason, timestamp]
        df.to_excel(EXCEL_FILE, index=False)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
