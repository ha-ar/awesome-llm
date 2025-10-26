# Quran Recitation Mistake Detection Guide

## Overview

This system identifies and highlights mistakes in Quran recitation by comparing transcribed audio with the correct Quranic text.

## How It Works

### 1. **Real-time Transcription**
- Audio is captured from microphone
- Whisper model transcribes in real-time
- Text is accumulated as you recite

### 2. **Mistake Detection**
- Click "Check for Mistakes" button
- System compares your recitation with correct Quran text
- Identifies word-level differences

### 3. **Visual Feedback**
The system highlights mistakes using colors:

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 **Green** | Correct word | Word matches perfectly |
| 🔴 **Red** | Wrong word | Said different word (hover to see correct) |
| 🟡 **Yellow** | Missing word | You skipped a word |
| 🟠 **Orange** | Extra word | You added a word that shouldn't be there |

## Usage Instructions

### Step 1: Start Recording
1. Click "Start Audio Input"
2. Begin reciting Quran verses clearly
3. Watch the transcription appear in real-time

### Step 2: Check for Mistakes
1. After reciting, click "Check for Mistakes"
2. Optionally, enter the verse reference (e.g., "1:1" for Al-Fatiha verse 1)
3. If you leave it empty, the system will auto-detect the verse

### Step 3: Review Results
- **Highlighted Text**: Shows color-coded mistakes
- **Accuracy Score**: Overall percentage of correct words
- **Detailed Report**: Lists all mistakes with suggestions

## Verse Reference Format

Use the format: `surah:ayah`

Examples:
- `1:1` = Surah Al-Fatiha, Verse 1
- `2:255` = Surah Al-Baqarah, Verse 255 (Ayat al-Kursi)
- `112:1` = Surah Al-Ikhlas, Verse 1

## Types of Mistakes Detected

### 1. **Wrong Words**
- **What**: You said a different word
- **Display**: Red highlight with correct word in tooltip
- **Example**: Said "الرحمن" instead of "الرَّحْمَٰنِ"

### 2. **Missing Words**
- **What**: You skipped a word
- **Display**: Yellow highlight showing the missing word
- **Example**: Forgot "وَإِيَّاكَ" in verse

### 3. **Extra Words**
- **What**: You added a word that shouldn't be there
- **Display**: Orange highlight with strikethrough
- **Example**: Repeated a word accidentally

### 4. **Pronunciation Variations**
- The system normalizes certain Arabic characters:
  - Alef variants (أ، إ، آ → ا)
  - Teh marbuta (ة → ه)
  - Diacritical marks are compared separately

## Accuracy Scoring

The accuracy score is calculated as:

```
Accuracy = (Correct Words / Total Words) × 100%
```

**Interpretation:**
- **90-100%**: Excellent! Minor improvements needed
- **75-89%**: Good, but review highlighted mistakes
- **60-74%**: Fair, practice the verse more
- **Below 60%**: Needs significant practice

## Current Limitations

### 1. **Limited Verse Database**
Currently supports sample verses:
- Surah Al-Fatiha (1:1-7)
- Beginning of Surah Al-Baqarah (2:1-3)

**Solution**: Expand database or use API (see below)

### 2. **Auto-Detection Accuracy**
Auto-detection works best when:
- You recite complete verses
- Audio quality is good
- Pronunciation is clear

### 3. **Diacritics (Tashkeel)**
- System can compare with or without diacritics
- Some diacritical differences may not be caught
- Focus is on word accuracy, not perfect harakat

## Expanding the Database

### Option 1: Add More Verses Manually

Edit `quran_checker.py` and add to `_load_quran_sample()`:

```python
def _load_quran_sample(self) -> Dict[str, str]:
    return {
        "1:1": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        # Add more verses here
        "2:255": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...",
    }
```

### Option 2: Use Quran API

The code includes a function to load from API:

```python
from quran_checker import load_quran_from_api

# Load entire Surah Al-Fatiha
quran_text = load_quran_from_api(surah=1)

# Load specific verse
quran_text = load_quran_from_api(surah=2, ayah=255)
```

**Available APIs:**
- https://api.alquran.cloud/v1/
- https://quranenc.com/api/
- https://cdn.jsdelivr.net/npm/quran-json@3/

### Option 3: Use Local Quran Database

Download a complete Quran text file (JSON or SQLite) and load it:

```python
import json

def _load_quran_from_file(self, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Process and return as dict
```

## Advanced Features

### 1. **Tajweed Rule Detection** (Future)
- Detect mispronunciation of specific letters
- Check for proper Ghunnah, Idgham, etc.
- Requires specialized model

### 2. **Pronunciation Scoring** (Future)
- Beyond word accuracy, check pronunciation quality
- Use phoneme-level analysis
- Requires additional training data

### 3. **Learning Mode**
- Practice specific verses repeatedly
- Track improvement over time
- Personalized feedback

## Troubleshooting

### Issue: "No matching verse found"
**Solutions:**
- Specify the verse reference manually
- Expand the verse database
- Ensure you're reciting complete verses

### Issue: Many false positives
**Causes:**
- Poor audio quality
- Background noise
- Unclear pronunciation

**Solutions:**
- Use a better microphone
- Recite in quiet environment
- Speak more clearly

### Issue: Diacritics not matching
**Note:** The system currently focuses on word accuracy.
For diacritical precision:
- Use the Mishkal output
- Compare manually with Mushaf

### Issue: System too strict/lenient
**Adjustment:**
Modify the normalization in `quran_checker.py`:

```python
def normalize_arabic(self, text: str) -> str:
    # Adjust what to ignore/compare
    # More normalization = more lenient
    # Less normalization = stricter
```

## Best Practices

### For Accurate Detection:
1. ✅ Recite complete verses
2. ✅ Use good quality microphone
3. ✅ Minimize background noise
4. ✅ Speak clearly and at moderate pace
5. ✅ Specify verse reference when known

### For Learning:
1. 📚 Start with short surahs (Al-Fatiha, Al-Ikhlas)
2. 🔁 Practice same verse multiple times
3. 📊 Track accuracy improvement
4. ✍️ Note common mistakes
5. 🎯 Focus on problematic words

## API Integration Example

To add all verses of a Surah automatically:

```python
import requests
from quran_checker import QuranMistakeChecker

def load_full_surah(surah_number):
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}"
    response = requests.get(url)
    data = response.json()
    
    if data['code'] == 200:
        verses = {}
        for ayah in data['data']['ayahs']:
            ref = f"{surah_number}:{ayah['numberInSurah']}"
            verses[ref] = ayah['text']
        return verses
    return {}

# Usage
checker = QuranMistakeChecker()
# Load Al-Fatiha
checker.quran_text.update(load_full_surah(1))
# Load Al-Baqarah
checker.quran_text.update(load_full_surah(2))
```

## Performance Tips

### For Faster Checking:
- Pre-load common surahs at startup
- Cache verse lookups
- Use indexed database for large collections

### For Better Accuracy:
- Use the Quran-specific Whisper model (already configured)
- Ensure good audio quality (16kHz sample rate)
- Practice with verses you know well first

## Contributing

To improve the mistake detection:

1. **Add more verses** to the database
2. **Improve normalization** rules
3. **Add Tajweed rules** detection
4. **Create test cases** with known mistakes
5. **Optimize comparison algorithm**

## References

- Quran API: https://alquran.cloud/api
- Tarteel AI: https://www.tarteel.ai/
- Tajweed Rules: https://tajweed.me/
- Arabic Text Processing: https://github.com/linuxscout/
