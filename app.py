from flask import Flask, render_template, request, jsonify, send_file
import openai
from gtts import gTTS
import os
from io import BytesIO
from difflib import SequenceMatcher

app = Flask(__name__)

# Add these lines right after app initialization
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

openai.api_key = ""  # Configurar la API Key en variable de entorno

MONOLOGUE = """
Dogs are loyal and friendly animals. They love to play, run, and spend time with their owners. 
Many people consider dogs to be part of their family. 
They can be trained to follow commands and even help people with disabilities.
"""

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/monologo')
def monologo():
    try:
        # Generate new monologue using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates short English texts."},
                {"role": "user", "content": "Generate a meaningful paragraph in English about the topic of airplanes. Maximum 10 words."}
            ]
        )
        english_text = response.choices[0].message.content.strip()
        
        # Generate Spanish translation
        translation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator from English to Spanish."},
                {"role": "user", "content": f"Translate this text to Spanish: {english_text}"}
            ]
        )
        spanish_text = translation_response.choices[0].message.content.strip()
        
        return render_template('monologo.html', english_text=english_text, spanish_text=spanish_text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translate_word', methods=['POST'])
def translate_word():
    """Traduce una palabra y proporciona un ejemplo de uso en inglés."""
    data = request.get_json()
    word = data.get('word', '')
    
    if not word:
        return jsonify({"error": "No se proporcionó una palabra"})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator. Provide the Spanish translation and an example sentence in English."},
                {"role": "user", "content": f"Translate the word '{word}' to Spanish and provide a simple example sentence using this word."}
            ]
        )
        translation = response.choices[0].message.content
        return jsonify({"translation": translation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        audio_io = BytesIO()
        
        # For normal speed, we use regular gTTS without modifications
        tts = gTTS(text=text, lang='en', slow=False)
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        return send_file(
            audio_io,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name='speech.mp3'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No se envió audio"}), 400

    audio = request.files["audio"]
    if audio.filename == "":
        return jsonify({"error": "Archivo no válido"}), 400

    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio.filename)
    audio.save(audio_path)

    try:
        with open(audio_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            transcription = response.text
            # Compare with the text from the page (sent in the request)
            original_text = request.form.get('original_text', '')
            similitud = compare_texts(transcription, original_text)
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({"transcription": transcription, "similitud": similitud})

    except Exception as e:
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
        return jsonify({"error": str(e)}), 500

@app.route('/generate_practice_sentences')
def generate_practice_sentences():
    try:
        prompt = ("Generate 4 simple English sentences at A1 level for listening practice. "
                 "Each sentence should be a statement about airplanes, simple and brief. "
                 "Return them in JSON format only. "
                 '{"text1": "sentence1", "text2": "sentence2", "text3": "sentence3", "text4": "sentence4"}')

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        json_generated = response.choices[0].message["content"].strip()
        texts = eval(json_generated)
        return jsonify(texts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_slow_audio', methods=['POST'])
def generate_slow_audio():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        audio_io = BytesIO()
        # For slow speed, we use the punctuation trick
        modified_text = text.replace(' ', '. ') # This trick makes gTTS read more deliberately
        tts = gTTS(text=modified_text, lang='en', slow=False)
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        return send_file(
            audio_io,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name='speech_slow.mp3'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    original_text = data.get("original_text", "").lower()
    user_text = data.get("user_text", "").lower()
    
    # Using SequenceMatcher to calculate similarity between texts
    similarity = SequenceMatcher(None, original_text, user_text).ratio()
    
    # Convert to percentage and round to 2 decimal places
    score = round(similarity * 100, 2)
    
    return jsonify({"score": score})

def compare_texts(text1, text2):
    # Normalize and convert to lowercase for better comparison
    text1 = text1.strip().lower()
    text2 = text2.strip().lower()

    # Compare texts and calculate similarity
    similarity = SequenceMatcher(None, text1, text2).ratio()

    # Convert similarity from 0-1 to 0-10 scale
    score = round(similarity * 10, 2)
    return score

if __name__ == '__main__':
    app.run(debug=True, port=12345)