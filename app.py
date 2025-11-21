import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pypdf
from upsc_essay import workflow  # Import the workflow from your existing script

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def extract_text_from_pdf(file_stream):
    try:
        pdf_reader = pypdf.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    essay_text = ""
    
    # Check if a file was uploaded
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file.filename.lower().endswith('.pdf'):
            essay_text = extract_text_from_pdf(file)
        else:
            return jsonify({'error': 'Only PDF files are supported for upload.'}), 400
    # Check if text was pasted
    elif 'essay_text' in request.form and request.form['essay_text'].strip() != '':
        essay_text = request.form['essay_text']
    else:
        return jsonify({'error': 'Please provide an essay via text or PDF upload.'}), 400

    if not essay_text.strip():
         return jsonify({'error': 'Could not extract text from the input.'}), 400

    try:
        # Invoke the LangGraph workflow
        initial_state = {'essay': essay_text}
        result = workflow.invoke(initial_state)
        
        # The result contains the final state. We can return the whole thing or specific parts.
        # Based on upsc-essay.py, the state has: 
        # language_feedback, analysis_feedback, clarity_feedback, overall_feedback, avg_score
        
        response_data = {
            'language_feedback': result.get('language_feedback'),
            'analysis_feedback': result.get('analysis_feedback'),
            'clarity_feedback': result.get('clarity_feedback'),
            'overall_feedback': result.get('overall_feedback'),
            'avg_score': result.get('avg_score'),
            'individual_scores': result.get('individual_scores')
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': f'An error occurred during evaluation: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
