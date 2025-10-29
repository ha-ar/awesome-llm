# assets/python/quran_core.py
"""
Core Quran analysis module optimized for Flutter integration
Includes: Transcription, Mistake Detection, Tajweed Analysis
"""

import json
import sqlite3
import numpy as np
import torch
from transformers import pipeline
from pathlib import Path
import tempfile
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Initialize paths for mobile environment
SCRIPT_DIR = Path(__file__).parent
QURAN_DB_PATH = SCRIPT_DIR / "quran.db"
MODEL_CACHE_DIR = SCRIPT_DIR / "models"

# Global model instance (loaded once)
_whisper_model = None
_model_loaded = False

@dataclass
class AnalysisResult:
    """Complete analysis result structure"""
    transcription: str
    word_accuracy: float
    tajweed_score: float
    total_mistakes: int
    tajweed_mistakes: int
    highlighted_text: str
    mistake_details: List[Dict]
    tajweed_details: List[Dict]
    verse_reference: str
    processing_time: float

class QuranAnalyzer:
    """Main analyzer class optimized for mobile performance"""
    
    def __init__(self):
        self.db_path = QURAN_DB_PATH
        self._init_database()
        self._load_tajweed_rules()
        
    def _init_database(self):
        """Initialize local SQLite database"""
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tajweed_rules (
                rule_name TEXT PRIMARY KEY,
                pattern TEXT,
                description TEXT,
                severity TEXT
            )
        ''')
        
        # Create indexes for fast lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_verse_text ON verses(text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_surah_ayah ON verses(surah, ayah)')
        
        conn.commit()
        conn.close()
    
    def load_whisper_model(self):
        """Load Whisper model once for reuse"""
        global _whisper_model, _model_loaded
        
        if _model_loaded and _whisper_model:
            return _whisper_model
            
        try:
            print("🔄 Loading Whisper model for mobile...")
            
            # Use smaller, faster model for mobile
            model_id = "openai/whisper-small"  # Much smaller than large-v3
            # Alternative: "deepdml/whisper-large-v3-turbo-ar-quran-mix" if space allows
            
            device = "cpu"  # Mobile devices typically use CPU
            torch_dtype = torch.float32
            
            _whisper_model = pipeline(
                "automatic-speech-recognition",
                model=model_id,
                torch_dtype=torch_dtype,
                device=device,
                model_kwargs={"cache_dir": str(MODEL_CACHE_DIR)}
            )
            
            _model_loaded = True
            print("✅ Whisper model loaded successfully")
            return _whisper_model
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file to Arabic text"""
        try:
            model = self.load_whisper_model()
            
            # Transcribe with Arabic language setting
            result = model(
                audio_path,
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
        """Clean and normalize Arabic text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize Arabic characters
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')  # Ta Marbutah normalization
        
        return text
    
    def analyze_complete(self, audio_path: str, verse_ref: str = "") -> AnalysisResult:
        """Complete analysis pipeline"""
        import time
        start_time = time.time()
        
        try:
            # 1. Transcription
            transcription = self.transcribe_audio(audio_path)
            if not transcription:
                return self._empty_result("Transcription failed")
            
            # 2. Find correct verse
            if not verse_ref:
                verse_ref = self._auto_detect_verse(transcription)
            
            correct_text = self.get_verse(verse_ref)
            if not correct_text:
                return self._empty_result(f"Verse {verse_ref} not found")
            
            # 3. Mistake analysis
            mistake_result = self._check_word_mistakes(transcription, correct_text)
            
            # 4. Tajweed analysis
            tajweed_result = self._check_tajweed_rules(transcription)
            
            # 5. Generate highlighted text
            highlighted_text = self._generate_highlighted_text(
                transcription, correct_text, mistake_result['mistakes']
            )
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                transcription=transcription,
                word_accuracy=mistake_result['accuracy'],
                tajweed_score=tajweed_result['score'],
                total_mistakes=len(mistake_result['mistakes']),
                tajweed_mistakes=len(tajweed_result['mistakes']),
                highlighted_text=highlighted_text,
                mistake_details=mistake_result['mistakes'],
                tajweed_details=tajweed_result['mistakes'],
                verse_reference=verse_ref,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return self._empty_result(f"Analysis failed: {str(e)}")
    
    def get_verse(self, reference: str) -> Optional[str]:
        """Get verse by reference (e.g., '1:1')"""
        try:
            if ':' not in reference:
                return None
                
            surah, ayah = map(int, reference.split(':'))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT text FROM verses WHERE surah = ? AND ayah = ?",
                (surah, ayah)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"❌ Error getting verse {reference}: {e}")
            return None
    
    def _auto_detect_verse(self, transcription: str) -> str:
        """Auto-detect verse by matching transcription"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get first few words for matching
            words = transcription.split()[:5]  # First 5 words
            
            if words:
                search_text = ' '.join(words)
                cursor.execute(
                    "SELECT surah, ayah, text FROM verses WHERE text LIKE ? LIMIT 1",
                    (f"%{search_text}%",)
                )
                
                result = cursor.fetchone()
                if result:
                    return f"{result[0]}:{result[1]}"
            
            conn.close()
            return "1:1"  # Default fallback
            
        except Exception as e:
            print(f"❌ Auto-detection error: {e}")
            return "1:1"
    
    def _check_word_mistakes(self, recited: str, correct: str) -> Dict:
        """Check word-level mistakes"""
        recited_words = recited.split()
        correct_words = correct.split()
        
        mistakes = []
        correct_count = 0
        
        # Simple word-by-word comparison
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
        
        # Check for missing words
        if len(correct_words) > len(recited_words):
            for i in range(len(recited_words), len(correct_words)):
                mistakes.append({
                    'position': i,
                    'recited': '',
                    'correct': correct_words[i],
                    'type': 'missing_word'
                })
        
        # Check for extra words  
        elif len(recited_words) > len(correct_words):
            for i in range(len(correct_words), len(recited_words)):
                mistakes.append({
                    'position': i,
                    'recited': recited_words[i],
                    'correct': '',
                    'type': 'extra_word'
                })
        
        total_words = max(len(recited_words), len(correct_words))
        accuracy = (correct_count / total_words * 100) if total_words > 0 else 0
        
        return {
            'accuracy': accuracy,
            'mistakes': mistakes,
            'total_words': total_words,
            'correct_words': correct_count
        }
    
    def _normalize_word(self, word: str) -> str:
        """Normalize Arabic word for comparison"""
        # Remove diacritics
        word = re.sub(r'[َُِّْٰٱًٌٍ]', '', word)
        # Normalize alef forms
        word = word.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        return word.strip()
    
    def _check_tajweed_rules(self, text: str) -> Dict:
        """Fast Tajweed rule checking"""
        mistakes = []
        
        # Define core Tajweed patterns
        rules = [
            {
                'name': 'Ghunnah',
                'pattern': r'[نم]ّ',
                'severity': 'major',
                'description': 'Requires nasal sound for 2 counts'
            },
            {
                'name': 'Qalqalah', 
                'pattern': r'[قطبجد]ْ',
                'severity': 'major',
                'description': 'Requires echoing/bouncing sound'
            },
            {
                'name': 'Madd',
                'pattern': r'[اوي]ء',
                'severity': 'major', 
                'description': 'Requires elongation'
            },
            {
                'name': 'Idgham',
                'pattern': r'نْ[يرملون]',
                'severity': 'major',
                'description': 'Letters should merge'
            }
        ]
        
        words = text.split()
        
        for word_idx, word in enumerate(words):
            for rule in rules:
                matches = re.finditer(rule['pattern'], word)
                for match in matches:
                    mistakes.append({
                        'rule': rule['name'],
                        'word': word,
                        'position': word_idx,
                        'severity': rule['severity'],
                        'description': rule['description'],
                        'match': match.group()
                    })
        
        # Calculate Tajweed score
        total_deductions = len(mistakes) * 5  # 5 points per mistake
        tajweed_score = max(0, 100 - total_deductions)
        
        return {
            'score': tajweed_score,
            'mistakes': mistakes,
            'total_rules_checked': len(rules)
        }
    
    def _generate_highlighted_text(self, recited: str, correct: str, mistakes: List[Dict]) -> str:
        """Generate HTML highlighted text"""
        recited_words = recited.split()
        correct_words = correct.split()
        highlighted_words = []
        
        max_len = max(len(recited_words), len(correct_words))
        
        for i in range(max_len):
            if i < len(recited_words) and i < len(correct_words):
                recited_word = recited_words[i]
                correct_word = correct_words[i]
                
                # Check if this position has a mistake
                mistake = next((m for m in mistakes if m['position'] == i), None)
                
                if mistake:
                    if mistake['type'] == 'wrong_word':
                        highlighted_words.append(f'<span style="color: red; font-weight: bold;">{recited_word}</span>')
                    elif mistake['type'] == 'missing_word':
                        highlighted_words.append(f'<span style="color: orange; background-color: yellow;">[{correct_word}]</span>')
                    else:
                        highlighted_words.append(recited_word)
                else:
                    highlighted_words.append(f'<span style="color: green;">{recited_word}</span>')
            
            elif i >= len(recited_words):  # Missing word
                highlighted_words.append(f'<span style="color: orange; background-color: yellow;">[{correct_words[i]}]</span>')
            
            else:  # Extra word
                highlighted_words.append(f'<span style="color: red; text-decoration: line-through;">{recited_words[i]}</span>')
        
        return ' '.join(highlighted_words)
    
    def _empty_result(self, error_message: str) -> AnalysisResult:
        """Return empty result with error"""
        return AnalysisResult(
            transcription="",
            word_accuracy=0.0,
            tajweed_score=0.0,
            total_mistakes=0,
            tajweed_mistakes=0,
            highlighted_text=error_message,
            mistake_details=[],
            tajweed_details=[],
            verse_reference="",
            processing_time=0.0
        )
    
    def _load_tajweed_rules(self):
        """Load Tajweed rules into database"""
        # This would be called during setup
        pass

# Main function for Flutter integration
def analyze_audio_file(audio_path: str, verse_ref: str = "") -> str:
    """
    Main entry point for Flutter
    Returns JSON string with complete analysis
    """
    try:
        analyzer = QuranAnalyzer()
        result = analyzer.analyze_complete(audio_path, verse_ref)
        return json.dumps(asdict(result), ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "error": str(e),
            "transcription": "",
            "word_accuracy": 0.0,
            "tajweed_score": 0.0
        }
        return json.dumps(error_result, ensure_ascii=False)

def get_verse_text(reference: str) -> str:
    """Get verse text by reference"""
    try:
        analyzer = QuranAnalyzer()
        verse = analyzer.get_verse(reference)
        return json.dumps({"verse": verse or "", "reference": reference}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e), "verse": "", "reference": reference}, ensure_ascii=False)

# Initialize for Flutter when imported
if __name__ == "__main__":
    print("Quran Core Module loaded successfully")