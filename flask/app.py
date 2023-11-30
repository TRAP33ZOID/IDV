from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF
import openai
import os
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

def extract_text_pymupdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def summarize_text(text):
    openai.api_key = ''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": '''Summarize the following text fron an insurance policy:
             try to take the following into consideration
                 Type of Insurance
        Question: "Can you identify and describe the type of insurance covered in this policy? For example, is it Home, Auto, or Life insurance, and what are the key characteristics of this type?"

    Category of Coverage
        Question: "What are the different categories of coverage included in this policy? Please describe each category, such as Dwelling, Personal Property, or Liability, and their specific coverage details."

    What's Covered
        Question: "Could you list and elaborate on the specific items, scenarios, or risks that are covered under this policy? Please include detailed information like coverage limits, conditions, and any specific terms mentioned."

    What's Not Covered
        Question: "What are the exclusions and limitations of this policy? I'm interested in knowing what scenarios, items, or risks are specifically not covered, along with any exceptions or additional text that provides context to these exclusions."

    Events Covered
        Question: "Which events or circumstances does this policy cover? Please provide a comprehensive list of events like Fire, Theft, or Natural Disasters, and include any clarifications or exceptions associated with these covered events."

    Additional Details
        Question: "Are there any additional details, hover-over texts, or clarifications provided in the policy that are important to understand its coverage, exclusions, or events covered? If so, please provide these details for a more comprehensive understanding of the policy."''' },
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            # Save the file stream to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            # Process the PDF file
            extracted_text = extract_text_pymupdf(temp_file_path)

            # Summarize the text
            summary = summarize_text(extracted_text)
            os.unlink(temp_file_path)  # Remove the temporary file
            return jsonify({"summary": summary, "extractedText": extracted_text[:500]})
        else:
            return jsonify({"error": "Invalid file type or no file uploaded"}), 400
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)