"""
Quran Recitation Mistake Checker
This module compares recited text with correct Quranic text and highlights mistakes.
"""

import re
from difflib import SequenceMatcher
from typing import List, Tuple, Dict, Optional
import os
from quran_api import QuranAPI

class QuranMistakeChecker:
    """
    Class to check for mistakes in Quran recitation by comparing
    transcribed text with the correct Quranic verse.
    """
    
    def __init__(self, data_dir: str = "quran_data"):
        """Initialize the mistake checker with Quran text data."""
        self.api = QuranAPI(data_dir)
        self.quran_text = self._load_quran_data()
        
    def _load_quran_data(self) -> Dict[str, str]:
        """Load Quran data from local storage or fallback to sample"""
        
        # Try to load from local data first
        if self.api.is_data_available():
            print("📚 Loading Quran data from local storage...")
            try:
                data = self.api.load_local_quran()
                if data:
                    return self._convert_api_data_to_dict(data)
            except Exception as e:
                print(f"⚠️ Error loading local data: {e}")
        
        print("📝 Using sample Quran data. Run 'python setup_quran_data.py' for complete data.")
        return self._load_quran_sample()
    
    def _convert_api_data_to_dict(self, data: Dict) -> Dict[str, str]:
        """Convert API format to reference:text format"""
        verses = {}

        try:
            surahs = data.get('surahs', [])

            for surah_data in surahs:
                surah_num = surah_data.get('number')

                for ayah_data in surah_data.get('ayahs', []):
                    ayah_num = ayah_data.get('numberInSurah')
                    ayah_text = ayah_data.get('text', '')

                    if surah_num and ayah_num and ayah_text:
                        reference = f"{surah_num}:{ayah_num}"
                        verses[reference] = ayah_text

            print(f"✅ Loaded {len(verses)} verses from local data")
            return verses

        except Exception as e:
            print(f"❌ Error converting API data: {e}")
            return self._load_quran_sample()

    def _load_quran_sample(self) -> Dict[str, str]:
        """Load sample Quran verses for fallback when full data is unavailable."""
        return {
            "1:1": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "1:2": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            "1:3": "الرَّحْمَٰنِ الرَّحِيمِ",
            "1:4": "مَالِكِ يَوْمِ الدِّينِ",
            "1:5": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
            "1:6": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
            "1:7": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"
        }

    def get_verse_by_reference(self, reference: str) -> Optional[str]:
        """Get verse by reference (e.g., '1:1')"""
        if reference in self.quran_text:
            return self.quran_text[reference]
        
        # Try to get from API if not in loaded data
        try:
            parts = reference.split(':')
            if len(parts) == 2:
                surah, ayah = int(parts[0]), int(parts[1])
                verse = self.api.get_verse(surah, ayah)
                if verse:
                    # Cache it for future use
                    self.quran_text[reference] = verse
                    return verse
        except Exception as e:
            print(f"⚠️ Error getting verse {reference}: {e}")
        
        return None
    
    def search_verses(self, text: str, limit: int = 5) -> List[Dict]:
        """Search for verses containing the text"""
        return self.api.search_verses(text, limit)
    
    def normalize_arabic(self, text: str) -> str:
        """
        Normalize Arabic text by removing diacritics and standardizing characters.
        This helps in comparison by ignoring tashkeel differences.
        """
        # Remove all Arabic diacritical marks
        diacritics = re.compile(r'[\u064B-\u065F\u0670]')  # All harakat
        text = diacritics.sub('', text)
        
        # Normalize alef variants
        text = re.sub('[إأآا]', 'ا', text)
        
        # Normalize teh marbuta
        text = re.sub('ة', 'ه', text)
        
        # Remove tatweel (kashida)
        text = re.sub('ـ', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def find_best_match(self, recited_text: str) -> Tuple[str, str, float]:
        """
        Find the best matching verse from the Quran for the recited text.
        Returns: (verse_ref, correct_text, similarity_score)
        """
        normalized_recited = self.normalize_arabic(recited_text)
        best_match = ("", "", 0.0)
        
        for verse_ref, correct_text in self.quran_text.items():
            normalized_correct = self.normalize_arabic(correct_text)
            
            # Calculate similarity ratio
            similarity = SequenceMatcher(None, normalized_recited, normalized_correct).ratio()
            
            if similarity > best_match[2]:
                best_match = (verse_ref, correct_text, similarity)
        
        return best_match
    
    def get_word_level_diff(self, recited: str, correct: str) -> List[Tuple[str, str, str]]:
        """
        Compare recited and correct text word by word.
        Returns list of (word, status, correct_word) where status is:
        - 'correct': Word matches
        - 'wrong': Word doesn't match
        - 'missing': Word missing from recitation
        - 'extra': Extra word in recitation
        """
        recited_words = recited.split()
        correct_words = correct.split()
        
        # Use SequenceMatcher for alignment
        matcher = SequenceMatcher(None, recited_words, correct_words)
        differences = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Words match
                for i in range(i1, i2):
                    differences.append((recited_words[i], 'correct', correct_words[j1 + (i - i1)]))
            elif tag == 'replace':
                # Words are different
                for i in range(i1, i2):
                    correct_idx = j1 + (i - i1) if j1 + (i - i1) < j2 else j2 - 1
                    differences.append((recited_words[i], 'wrong', correct_words[correct_idx]))
            elif tag == 'delete':
                # Extra words in recitation
                for i in range(i1, i2):
                    differences.append((recited_words[i], 'extra', ''))
            elif tag == 'insert':
                # Missing words from recitation
                for j in range(j1, j2):
                    differences.append(('', 'missing', correct_words[j]))
        
        return differences
    
    def highlight_mistakes_html(self, recited: str, correct: str) -> str:
        """
        Generate HTML with highlighted mistakes.
        Green = correct, Red = wrong, Yellow = missing, Orange = extra
        """
        word_diffs = self.get_word_level_diff(recited, correct)
        
        html_parts = ['<div style="font-size: 24px; line-height: 2; direction: rtl; text-align: right;">']
        
        for word, status, correct_word in word_diffs:
            if status == 'correct':
                html_parts.append(f'<span style="color: green; font-weight: bold;">{word}</span> ')
            elif status == 'wrong':
                html_parts.append(
                    f'<span style="background-color: #ffcccc; color: red; font-weight: bold; '
                    f'padding: 2px 4px; border-radius: 3px;" '
                    f'title="Should be: {correct_word}">{word}</span> '
                )
            elif status == 'missing':
                html_parts.append(
                    f'<span style="background-color: #ffffcc; color: orange; font-weight: bold; '
                    f'padding: 2px 4px; border-radius: 3px; text-decoration: underline;">'
                    f'[{correct_word}]</span> '
                )
            elif status == 'extra':
                html_parts.append(
                    f'<span style="background-color: #fff3cd; color: #856404; font-weight: bold; '
                    f'padding: 2px 4px; border-radius: 3px; text-decoration: line-through;">{word}</span> '
                )
        
        html_parts.append('</div>')
        return ''.join(html_parts)
    
    def generate_mistake_report(self, recited: str, correct: str, verse_ref: str) -> str:
        """
        Generate a detailed mistake report.
        """
        word_diffs = self.get_word_level_diff(recited, correct)
        
        total_words = len([d for d in word_diffs if d[1] != 'missing'])
        correct_count = len([d for d in word_diffs if d[1] == 'correct'])
        wrong_count = len([d for d in word_diffs if d[1] == 'wrong'])
        missing_count = len([d for d in word_diffs if d[1] == 'missing'])
        extra_count = len([d for d in word_diffs if d[1] == 'extra'])
        
        accuracy = (correct_count / total_words * 100) if total_words > 0 else 0
        
        report = f"""
📊 **Recitation Report for {verse_ref}**

✅ Correct words: {correct_count}
❌ Wrong words: {wrong_count}
⚠️ Missing words: {missing_count}
🔸 Extra words: {extra_count}

📈 Accuracy: {accuracy:.1f}%

---

**Correct verse:**
{correct}

**Your recitation:**
{recited}

---

**Mistakes Details:**
"""
        
        for word, status, correct_word in word_diffs:
            if status == 'wrong':
                report += f"\n❌ Said '{word}' but should be '{correct_word}'"
            elif status == 'missing':
                report += f"\n⚠️ Missing word: '{correct_word}'"
            elif status == 'extra':
                report += f"\n🔸 Extra word: '{word}'"
        
        return report
    
    def check_recitation(self, recited_text: str, expected_verse_ref: Optional[str] = None) -> Dict:
        """
        Main function to check recitation for mistakes.
        
        Args:
            recited_text: The transcribed recitation
            expected_verse_ref: Optional specific verse reference (e.g., "1:1")
        
        Returns:
            Dictionary with mistake analysis results
        """
        if expected_verse_ref and expected_verse_ref in self.quran_text:
            # Check against specific verse
            correct_text = self.quran_text[expected_verse_ref]
            verse_ref = expected_verse_ref
            similarity = SequenceMatcher(
                None, 
                self.normalize_arabic(recited_text), 
                self.normalize_arabic(correct_text)
            ).ratio()
        else:
            # Find best matching verse
            verse_ref, correct_text, similarity = self.find_best_match(recited_text)
        
        if not verse_ref:
            return {
                "found": False,
                "message": "Could not find matching verse in database"
            }
        
        # Generate detailed analysis
        highlighted_html = self.highlight_mistakes_html(recited_text, correct_text)
        report = self.generate_mistake_report(recited_text, correct_text, verse_ref)
        word_diffs = self.get_word_level_diff(recited_text, correct_text)
        
        total_words = len([d for d in word_diffs if d[1] != 'missing'])
        correct_count = len([d for d in word_diffs if d[1] == 'correct'])
        accuracy = (correct_count / total_words * 100) if total_words > 0 else 0
        
        return {
            "found": True,
            "verse_ref": verse_ref,
            "correct_text": correct_text,
            "recited_text": recited_text,
            "similarity": similarity,
            "accuracy": accuracy,
            "highlighted_html": highlighted_html,
            "report": report,
            "word_diffs": word_diffs
        }


def load_quran_from_api(surah: Optional[int] = None, ayah: Optional[int] = None) -> Dict[str, str]:
    """
    Load Quran text from API.
    Uses: https://api.alquran.cloud/v1/
    
    Example:
        load_quran_from_api(1)  # Load entire Surah Al-Fatiha
        load_quran_from_api(1, 1)  # Load specific verse
    """
    import requests
    
    quran_dict = {}
    
    try:
        if surah and ayah:
            # Load specific verse
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}"
            response = requests.get(url)
            data = response.json()
            if data['code'] == 200:
                quran_dict[f"{surah}:{ayah}"] = data['data']['text']
        elif surah:
            # Load entire surah
            url = f"https://api.alquran.cloud/v1/surah/{surah}"
            response = requests.get(url)
            data = response.json()
            if data['code'] == 200:
                for ayah_data in data['data']['ayahs']:
                    ref = f"{surah}:{ayah_data['numberInSurah']}"
                    quran_dict[ref] = ayah_data['text']
        else:
            print("Please provide at least a surah number")
    except Exception as e:
        print(f"Error loading Quran from API: {e}")
    
    return quran_dict


# Example usage
if __name__ == "__main__":
    checker = QuranMistakeChecker()
    
    # Test case 1: Perfect recitation
    recited = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    result = checker.check_recitation(recited, "1:1")
    print(result['report'])
    
    # Test case 2: Recitation with mistake
    recited_wrong = "بِسْمِ اللَّهِ الرَّحْمَن الرَّحِيمِ"  # Missing alef maddah
    result = checker.check_recitation(recited_wrong, "1:1")
    print(result['report'])
