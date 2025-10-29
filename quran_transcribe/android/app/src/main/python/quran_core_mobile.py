# quran_core_mobile.py
"""
Lightweight Quran analysis module for mobile devices
Handles database operations and basic analysis without heavy ML dependencies
"""

import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Initialize paths for mobile environment
SCRIPT_DIR = Path(__file__).parent
QURAN_DB_PATH = SCRIPT_DIR / "quran.db"

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
    error: str = ""

class QuranAnalyzerMobile:
    """Lightweight analyzer for mobile - no ML dependencies"""
    
    def __init__(self):
        self.db_path = QURAN_DB_PATH
        self._init_database()
        
    def _init_database(self):
        """Initialize local SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
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
        
        # Create indexes for fast lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_verse_text ON verses(text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_surah_ayah ON verses(surah, ayah)')
        
        # Insert sample verses if database is empty
        cursor.execute('SELECT COUNT(*) FROM verses')
        if cursor.fetchone()[0] == 0:
            self._insert_sample_verses(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_sample_verses(self, cursor):
        """Insert sample Quran verses"""
        sample_verses = {
            "1:1": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "1:2": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            "1:3": "الرَّحْمَٰنِ الرَّحِيمِ",
            "1:4": "مَالِكِ يَوْمِ الدِّينِ",
            "1:5": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
            "1:6": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
            "1:7": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
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
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics"""
        return re.sub(r'[َُِّْٰٱًٌٍ]', '', text)
    
    def analyze_with_transcription(self, transcription: str, verse_ref: str = "") -> Dict:
        """
        Analyze pre-transcribed text (transcription done by server or device)
        This is the lightweight mobile approach
        """
        import time
        start_time = time.time()
        
        try:
            if not transcription:
                return self._empty_result("No transcription provided")
            
            # Find correct verse
            if not verse_ref:
                verse_ref = self._auto_detect_verse(transcription)
            
            correct_text = self.get_verse(verse_ref)
            if not correct_text:
                return self._empty_result(f"Verse {verse_ref} not found")
            
            # Mistake analysis
            mistake_result = self._check_word_mistakes(transcription, correct_text)
            
            # Tajweed analysis
            tajweed_result = self._check_tajweed_rules(transcription)
            
            # Generate highlighted text
            highlighted_text = self._generate_highlighted_text(
                transcription, correct_text, mistake_result['mistakes']
            )
            
            processing_time = time.time() - start_time
            
            result = AnalysisResult(
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
            
            return asdict(result)
            
        except Exception as e:
            return self._empty_result(f"Analysis failed: {str(e)}")
    
    def get_verse(self, reference: str) -> Optional[str]:
        """Get verse by reference (e.g., '1:1')"""
        try:
            if ':' not in reference:
                return None
                
            surah, ayah = map(int, reference.split(':'))
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT text FROM verses WHERE surah = ? AND ayah = ?",
                (surah, ayah)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            return None
    
    def _auto_detect_verse(self, transcription: str) -> str:
        """Auto-detect verse by matching transcription"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get first few words for matching
            words = transcription.split()[:5]
            
            if words:
                search_text = ' '.join(words)
                cursor.execute(
                    "SELECT surah, ayah FROM verses WHERE text LIKE ? LIMIT 1",
                    (f"%{search_text}%",)
                )
                
                result = cursor.fetchone()
                if result:
                    return f"{result[0]}:{result[1]}"
            
            conn.close()
            return "1:1"  # Default fallback
            
        except Exception:
            return "1:1"
    
    def _check_word_mistakes(self, recited: str, correct: str) -> Dict:
        """Check word-level mistakes"""
        recited_words = recited.split()
        correct_words = correct.split()
        
        mistakes = []
        correct_count = 0
        
        # Word-by-word comparison
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
            'mistakes': mistakes
        }
    
    def _normalize_word(self, word: str) -> str:
        """Normalize Arabic word for comparison"""
        word = re.sub(r'[َُِّْٰٱًٌٍ]', '', word)
        word = word.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        return word.strip()
    
    def _check_tajweed_rules(self, text: str) -> Dict:
        """Fast Tajweed rule checking"""
        mistakes = []
        
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
                'description': 'Requires echoing sound'
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
                        'description': rule['description']
                    })
        
        tajweed_score = max(0, 100 - len(mistakes) * 5)
        
        return {
            'score': tajweed_score,
            'mistakes': mistakes
        }
    
    def _generate_highlighted_text(self, recited: str, correct: str, mistakes: List[Dict]) -> str:
        """Generate HTML highlighted text"""
        recited_words = recited.split()
        highlighted_words = []
        
        for i, word in enumerate(recited_words):
            mistake = next((m for m in mistakes if m['position'] == i), None)
            
            if mistake:
                highlighted_words.append(f'<span style="color: red;">{word}</span>')
            else:
                highlighted_words.append(f'<span style="color: green;">{word}</span>')
        
        return ' '.join(highlighted_words)
    
    def _empty_result(self, error_message: str) -> Dict:
        """Return empty result with error"""
        result = AnalysisResult(
            transcription="",
            word_accuracy=0.0,
            tajweed_score=0.0,
            total_mistakes=0,
            tajweed_mistakes=0,
            highlighted_text=error_message,
            mistake_details=[],
            tajweed_details=[],
            verse_reference="",
            processing_time=0.0,
            error=error_message
        )
        return asdict(result)

# Global analyzer instance
_analyzer = None

def get_analyzer():
    """Get or create analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = QuranAnalyzerMobile()
    return _analyzer

def analyze_audio(audio_path: str, verse_ref: str = "") -> str:
    """
    Analyze audio - for mobile, this expects transcription to be done externally
    Returns JSON string with analysis result or error
    """
    try:
        # For mobile lightweight version, return instruction to use server
        error_result = {
            "error": "Audio transcription requires server. Use analyze_text for pre-transcribed audio.",
            "transcription": "",
            "word_accuracy": 0.0,
            "tajweed_score": 0.0
        }
        return json.dumps(error_result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def analyze_text(transcription: str, verse_ref: str = "") -> str:
    """
    Analyze pre-transcribed text
    Main function for mobile use
    """
    try:
        analyzer = get_analyzer()
        result = analyzer.analyze_with_transcription(transcription, verse_ref)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def get_verse_text(reference: str) -> str:
    """Get verse text by reference"""
    try:
        analyzer = get_analyzer()
        verse = analyzer.get_verse(reference)
        return json.dumps({
            "verse": verse or "",
            "reference": reference
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "verse": "",
            "reference": reference
        }, ensure_ascii=False)
