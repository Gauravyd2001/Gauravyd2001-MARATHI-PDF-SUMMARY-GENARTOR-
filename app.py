import os
import string
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import PyPDF2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
from langdetect import detect
from googletrans import Translator
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import PyPDF2

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(pdf_file_path)  # Pass file path directly
        num_pages = len(reader.pages)
        if num_pages < 15:
            return None, "PDF must be at least 15 pages long."
        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if not text.strip():
            return None, "The PDF does not contain any text."
        detected_lang = detect(text)
        if detected_lang == 'mr':
            return text, None
        else:
            return None, "The content in the PDF is not in Marathi (मराठी) language."

def generate_summary(text):
    if text is None:
        return None
    
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count=3)  # Generating summary with 3 sentences
    
    # Filter out unwanted characters
    filtered_summary = []
    for sentence in summary:
        clean_sentence = re.sub(r'[^\w\s.,!?]', '', str(sentence))  # Keep only letters, numbers, spaces, punctuation
        filtered_summary.append(clean_sentence)
    
    summary_text = " ".join(filtered_summary)
    return summary_text

def generate_keywords(text):
    if text is None:
        return None
    # Removing punctuation except for dots (for sentence separation)
    text = text.translate(str.maketrans('', '', string.punctuation.replace('.', '')))
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    stop_words = set(stopwords.words('english'))
    # Removing stop words and keeping only nouns, plural nouns, and adjectives
    tagged = pos_tag(tokens)
    keywords = [word for word, pos in tagged if pos in ['NN', 'NNS', 'JJ'] and word.lower() not in stop_words]
    return keywords[:5]  # Taking first 5 keywords
def translate_summary(summary, target_language='en'):
    if summary is None:
        return None
    translator = Translator()
    translated_summary = translator.translate(summary, dest=target_language)
    return translated_summary.text

def translate_keywords(keywords, target_language='en'):
    if keywords is None:
        return None
    translator = Translator()
    translated_keywords = []
    for keyword in keywords:
        translated_keyword = translator.translate(keyword, dest=target_language)
        translated_keywords.append(translated_keyword.text)
    return translated_keywords

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                message = 'No selected file'
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                text, error_message = extract_text_from_pdf(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Pass file path
                if error_message:
                    message = error_message
                else:
                    summary = generate_summary(text)
                    keywords = generate_keywords(text)
                    return render_template('result.html', summary=summary, keywords=keywords)
            else:
                message = 'Invalid file type'
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)

