from flask import Flask, render_template, request
import os
import re
import pandas as pd
from docx2txt import process
from PyPDF2 import PdfReader

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text = ''
    for page in pdf_reader.pages:
       page_text = page.extract_text(pdf_path)
       text += page_text       
    return text

def extract_text_from_docx(docx_path):
     text = process(docx_path)
     return text

def extract_email_addresses(text):
    emails = re.findall(r'\b(?:E-Mailid-)?([A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,})\b', text)
    emails = [email.replace(' ', '') for email in emails]
    return emails

def extract_phone_numbers(text):
    phone_numbers = re.findall(r'\b(?:\d{10}|\d{9}|\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4}|\d{5}\s\d{5})\b', text)
    return list(set(phone_numbers))

def process_cv(cv_folder):
    data = []
    for filename in os.listdir(cv_folder):
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(os.path.join(cv_folder, filename))
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(os.path.join(cv_folder, filename))
        else:
            continue

        emails = extract_email_addresses(text)
        phones = extract_phone_numbers(text)
        email = ', '.join(emails) if emails else None
        phone = ', '.join(phones) if phones else None
        data.append({'Filename': filename, 'Email': email, 'Phone': phone})

    df = pd.DataFrame(data)
    df.to_excel('static/cv_info.xlsx', index=False)

@app.route('/', methods=['GET', 'POST'])
def upload_cv():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            if file.filename.endswith('.pdf') or file.filename.endswith('.docx'):
                file.save(os.path.join('uploads', file.filename))
        process_cv('uploads')
        return render_template('output.html', data=pd.read_excel('static/cv_info.xlsx').to_dict(orient='records'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
