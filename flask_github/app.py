from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import fitz  # PyMuPDF
import openai
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'C:\\Users\\Waleed\\Desktop\\website dev\\pdf'  # replace with your desired folder
ALLOWED_EXTENSIONS = {'pdf'}  # allowed file types

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.secret_key = 'your_very_secret_key_here'  # Replace with your secret key

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            #flash('You are now logged in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Wrong login credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    app.logger.debug(f"Logged in? {'logged_in' in session}")
    if not session.get('logged_in'):
        #flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/summarize', methods=['POST'])
def summarize():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check if file exists to avoid overwriting
        counter = 1
        while os.path.exists(save_path):
            name, extension = os.path.splitext(filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_{counter}{extension}")
            counter += 1

        file.save(save_path)

        extracted_text = extract_text_pymupdf(save_path)
        summary = summarize_text(extracted_text)
        os.unlink(save_path)  # Remove the file if you don't want to keep it after processing
        return jsonify({"summary": summary, "extractedText": extracted_text[:500]})
    else:
        return jsonify({"error": "Invalid file type or no file uploaded"}), 400

def extract_text_pymupdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def summarize_text(text):
    openai.api_key = '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'
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "Please summarize this text considering the following points: Type of Insurance, Category of Coverage, What's Covered, What's Not Covered, Events Covered, and Additional Details."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)
