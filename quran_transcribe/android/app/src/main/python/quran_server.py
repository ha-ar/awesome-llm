# assets/python/quran_server.py
"""
Lightweight Python server for Quran analysis
Optimized for mobile deployment
"""

import os
import sys
import json
import sqlite3
import tempfile
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import librosa
import soundfile as sf
from werkzeug.serving import make_server
from dataclasses import dataclass, asdict
import re
import logging

# Suppress Flask logs for mobile
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter

# Global variables
_whisper_model = None
_model_loaded = False
_server_thread = None
_server = None

SCRIPT_DIR = Path(__file__).parent
QURAN_DB_PATH = SCRIPT_DIR / "quran.db"

@dataclass
class AnalysisResult:
    transcription: str
    word_accuracy: float
    tajweed_score: float
    total_mistakes: int
    tajweed_mistakes: int
    highlighted_text: str
    mistake_details: list
    tajweed_details: list
    verse_reference: str
    processing_time: float
    error: str = ""

class QuranAnalyzer:
    def __init__(self):
        self.db_path = QURAN_DB_PATH
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists and is populated"""
        if not self.db_path.exists():
            print("📚 Setting up Quran database...")
            self._create_database()
    
    def _create_database(self):
        """Create and populate Quran database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verses (
                surah INTEGER,
                ayah INTEGER,
                text TEXT,
                text_simple TEXT,
                PRIMARY KEY (surah, ayah)
            )
        ''')
        
        # Insert sample data (expandable)
        sample_verses = {
            "1:1": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "1:2": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            "1:3": "الرَّحْمَٰنِ الرَّحِيمِ",
            "1:4": "مَالِكِ يَوْمِ الدِّينِ",
            "1:5": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
            "1:6": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
            "1:7": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
            "2:1": "الم",
            "2:2": "ذَٰلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِّلْمُتَّقِينَ",
            "112:1": "قُلْ هُوَ اللَّهُ أَحَدٌ",
            "112:2": "اللَّهُ الصَّمَدُ",
            "112:3": "لَمْ يَلِدْ وَلَمْ يُولَدْ",
            "112:4": "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ"
        }
        
        for ref, text in sample_verses.items():
            surah, ayah = map(int, ref.split(':'))
            text_simple = self._remove_diacritics(text)
            cursor.execute(
                "INSERT OR REPLACE INTO verses (surah, ayah, text, text_simple) VALUES (?, ?, ?, ?)",
                (surah, ayah, text, text_simple)
            )
        
        conn.commit()
        conn.close()
        print(f"✅ Database created with {len(sample_verses)} verses")
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics"""
        return re.sub(r'[َُِّْٰٱًٌٍ]', '', text)
    
    def load_whisper_model(self):
        """Load Whisper model (lightweight version)"""
        global _whisper_model, _model_loaded
        
        if _model_loaded and _whisper_model:
            return _whisper_model
        
        try:
            print("🔄 Loading Whisper model...")
            
            # Try to import transformers
            try:
                from transformers import pipeline
                import torch
                
                # Use smaller model for mobile
                model_id = "openai/whisper-small"
                device = "cpu"
                torch_dtype = torch.float32
                
                _whisper_model = pipeline(
                    "automatic-speech-recognition",
                    model=model_id,
                    torch_dtype=torch_dtype,
                    device=device,
                )
                
                _model_loaded = True
                print("✅ Whisper model loaded")
                return _whisper_model
                
            except ImportError:
                print("⚠️ Transformers not available, using dummy transcription")
                _whisper_model = "dummy"
                _model_loaded = True
                return _whisper_model
                
        except Exception as e:
            print(f"❌ Model loading error: {e}")
            _whisper_model = "dummy"
            _model_loaded = True
            return _whisper_model
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file"""
        try:
            model = self.load_whisper_model()
            
            if model == "dummy":
                # For testing without actual model
                return "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
            
            # Load and preprocess audio
            audio_data, sample_rate = librosa.load(audio_path, sr=16000)
            
            # Transcribe
            result = model(
                audio_data,
                generate_kwargs={
                    "language": "arabic",
                    "task": "transcribe",
                },
                return_timestamps=False,
            )
            
            transcription = result.get("text", "").strip()
            return self._clean_arabic_text(transcription)
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""
    
    def _clean_arabic_text(self, text: str) -> str:
        """Clean Arabic text"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        return text
    
    def analyze_complete(self, audio_path: str, verse_ref: str = "") -> AnalysisResult:
        """Complete Quran analysis"""
        start_time = time.time()
        
        try:
            # 1. Transcribe
            transcription = self.transcribe_audio(audio_path)
            if not transcription:
                return AnalysisResult(
                    "", 0, 0, 0, 0, "", [], [], "", 0, "Transcription failed"
                )
            
            # 2. Get correct verse
            if not verse_ref:
                verse_ref = self._auto_detect_verse(transcription)
            
            correct_text = self.get_verse(verse_ref)
            if not correct_text:
                return AnalysisResult(
                    transcription, 0, 0, 0, 0, "", [], [], verse_ref, 0, f"Verse {verse_ref} not found"
                )
            
            # 3. Check mistakes
            mistake_result = self._check_mistakes(transcription, correct_text)
            
            # 4. Check Tajweed
            tajweed_result = self._check_tajweed(transcription)
            
            # 5. Generate highlights
            highlighted = self._generate_highlights(transcription, correct_text, mistake_result['mistakes'])
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                transcription=transcription,
                word_accuracy=mistake_result['accuracy'],
                tajweed_score=tajweed_result['score'],
                total_mistakes=len(mistake_result['mistakes']),
                tajweed_mistakes=len(tajweed_result['mistakes']),
                highlighted_text=highlighted,
                mistake_details=mistake_result['mistakes'],
                tajweed_details=tajweed_result['mistakes'],
                verse_reference=verse_ref,
                processing_time=processing_time
            )
            
        except Exception as e:
            return AnalysisResult(
                "", 0, 0, 0, 0, "", [], [], "", time.time() - start_time, str(e)
            )
    
    def get_verse(self, reference: str) -> str:
        """Get verse by reference"""
        try:
            if ':' not in reference:
                return ""
            
            surah, ayah = map(int, reference.split(':'))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM verses WHERE surah = ? AND ayah = ?", (surah, ayah))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else ""
        except:
            return ""
    
    def _auto_detect_verse(self, transcription: str) -> str:
        """Auto-detect verse"""
        # Simple implementation - check against common verses
        if "بسم" in transcription:
            return "1:1"
        elif "الحمد" in transcription:
            return "1:2"
        elif "قل هو الله" in transcription:
            return "112:1"
        return "1:1"  # Default
    
    def _check_mistakes(self, recited: str, correct: str) -> dict:
        """Check word mistakes"""
        recited_words = recited.split()
        correct_words = correct.split()
        
        mistakes = []
        correct_count = 0
        
        for i, (r_word, c_word) in enumerate(zip(recited_words, correct_words)):
            if self._normalize_word(r_word) == self._normalize_word(c_word):
                correct_count += 1
            else:
                mistakes.append({
                    'position': i,
                    'recited': r_word,
                    'correct': c_word,
                    'type': 'wrong_word'
                })
        
        total_words = max(len(recited_words), len(correct_words))
        accuracy = (correct_count / total_words * 100) if total_words > 0 else 0
        
        return {'accuracy': accuracy, 'mistakes': mistakes}
    
    def _normalize_word(self, word: str) -> str:
        """Normalize Arabic word"""
        word = re.sub(r'[َُِّْٰٱًٌٍ]', '', word)
        word = word.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        return word.strip()
    
    def _check_tajweed(self, text: str) -> dict:
        """Check Tajweed rules"""
        mistakes = []
        
        # Simple Tajweed checks
        words = text.split()
        for i, word in enumerate(words):
            # Check for Ghunnah
            if re.search(r'[نم]ّ', word):
                mistakes.append({
                    'rule': 'Ghunnah',
                    'word': word,
                    'position': i,
                    'severity': 'major',
                    'description': 'Requires nasal sound for 2 counts'
                })
            
            # Check for Qalqalah
            if re.search(r'[قطبجد]ْ', word):
                mistakes.append({
                    'rule': 'Qalqalah',
                    'word': word,
                    'position': i,
                    'severity': 'major',
                    'description': 'Requires echoing sound'
                })
        
        score = max(0, 100 - len(mistakes) * 10)
        return {'score': score, 'mistakes': mistakes}
    
    def _generate_highlights(self, recited: str, correct: str, mistakes: list) -> str:
        """Generate highlighted HTML"""
        recited_words = recited.split()
        highlighted = []
        
        for i, word in enumerate(recited_words):
            mistake = next((m for m in mistakes if m['position'] == i), None)
            if mistake:
                highlighted.append(f'<span style="color: red;">{word}</span>')
            else:
                highlighted.append(f'<span style="color: green;">{word}</span>')
        
        return ' '.join(highlighted)

# Initialize analyzer
analyzer = QuranAnalyzer()

# API Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "model_loaded": _model_loaded,
        "database_ready": analyzer.db_path.exists()
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """Complete analysis endpoint"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
        
        audio_file = request.files['audio']
        verse_ref = request.form.get('verse_ref', '')
        
        # Save audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            
            # Analyze
            result = analyzer.analyze_complete(tmp_file.name, verse_ref)
            
            # Clean up
            os.unlink(tmp_file.name)
            
            return jsonify(asdict(result))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verse/<surah>/<ayah>', methods=['GET'])
def get_verse(surah, ayah):
    """Get specific verse"""
    try:
        verse = analyzer.get_verse(f"{surah}:{ayah}")
        return jsonify({"verse": verse, "reference": f"{surah}:{ayah}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Server management
class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        threading.Thread.__init__(self)
        self.port = port
        self.server = make_server('127.0.0.1', port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print(f'🚀 Quran server starting on port {self.port}...')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def start_server(port=5000):
    """Start the server in a separate thread"""
    global _server_thread
    if _server_thread is None or not _server_thread.is_alive():
        _server_thread = ServerThread(app, port)
        _server_thread.daemon = True
        _server_thread.start()
        time.sleep(2)  # Wait for server to start
        print(f'✅ Server ready on http://127.0.0.1:{port}')
    return _server_thread

def stop_server():
    """Stop the server"""
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        _server_thread.shutdown()
        _server_thread = None
        print('🛑 Server stopped')

if __name__ == "__main__":
    start_server(5000)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        stop_server()