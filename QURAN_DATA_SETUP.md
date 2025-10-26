# Quran Data Setup Guide

## Overview

This guide explains how to download and store complete Quran data locally for offline use in the recitation mistake detection system.

## Quick Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Quran Data
```bash
python setup_quran_data.py
```

### Step 3: Run the Application
```bash
python app.py
```

## Features

### 🌍 **Offline Access**
- Download once, use forever
- No internet required after setup
- Fast verse lookup

### 📚 **Complete Quran**
- All 114 Surahs
- 6,236+ Verses
- Multiple text editions available

### 🔍 **Smart Search**
- Find verses by text content
- Auto-detect recited verses
- Fuzzy matching for mistake detection

## Available Editions

| Edition | Description | Best For |
|---------|-------------|----------|
| **Uthmani** (Recommended) | Complete with Tashkeel/Diacritics | Precise mistake detection |
| **Simple** | Plain Arabic text | Basic comparison |
| **Enhanced Simple** | Improved simple text | Balanced approach |

## File Structure After Setup

```
quran_data/
├── quran_complete.json    # Complete Quran text (5-10 MB)
├── quran_metadata.json    # Statistics and info
└── surahs_info.json      # Surah metadata
```

## Usage Examples

### Basic Usage
```python
from quran_api import QuranAPI

# Initialize
api = QuranAPI()

# Get specific verse
verse = api.get_verse(surah=1, ayah=1)
print(verse)  # بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

# Search verses
results = api.search_verses("الرحمن")
for result in results:
    print(f"{result['reference']}: {result['text']}")
```

### Integration with Mistake Checker
```python
from quran_checker import QuranMistakeChecker

# Initialize (automatically uses local data)
checker = QuranMistakeChecker()

# Check mistakes
transcribed = "بسم الله الرحمن الرحيم"
result = checker.check_mistakes(transcribed, verse_ref="1:1")
print(f"Accuracy: {result['accuracy']:.1f}%")
```

## API Sources

The system uses multiple reliable Quran APIs:

1. **AlQuran.cloud API** (Primary)
   - URL: https://api.alquran.cloud/v1/
   - Most comprehensive
   - Multiple editions

2. **QuranEnc API** (Backup)
   - URL: https://quranenc.com/api/v1/
   - Alternative source

3. **jsDelivr CDN** (Fallback)
   - Fast CDN delivery
   - JSON format

## Troubleshooting

### Issue: Download Fails
**Solutions:**
- Check internet connection
- Try different edition
- Use manual download (see below)

### Issue: Large File Size
**Normal Sizes:**
- Uthmani: ~8-12 MB
- Simple: ~5-8 MB
- Enhanced: ~6-10 MB

**To reduce size:**
- Choose Simple edition
- Download specific Surahs only

### Issue: Slow Loading
**Solutions:**
- Use SSD storage
- Pre-load common Surahs
- Index frequently used verses

## Manual Download (Alternative)

If automatic download fails, you can manually download:

```bash
# Download complete Quran
curl "https://api.alquran.cloud/v1/quran/quran-uthmani" > quran_data/manual_quran.json

# Then load it
python -c "
from quran_api import QuranAPI
import json

api = QuranAPI()
with open('quran_data/manual_quran.json', 'r') as f:
    data = json.load(f)

if data.get('code') == 200:
    api._save_complete_quran(data['data'])
    print('✅ Manual setup complete!')
else:
    print('❌ Invalid data format')
"
```

## Advanced Configuration

### Custom Data Directory
```python
from quran_api import QuranAPI

# Use custom directory
api = QuranAPI(data_dir="my_quran_data")
api.download_complete_quran()
```

### Specific Surahs Only
```python
# Download only Al-Fatiha and Al-Baqarah
surahs_to_download = [1, 2]
for surah in surahs_to_download:
    api._download_surah_by_surah(surah)
```

### Custom Edition
```python
# Use different edition
custom_editions = [
    "quran-tajweed",      # With Tajweed rules
    "quran-wordbyword",   # Word by word
    "quran-kids"          # Simplified for children
]

for edition in custom_editions:
    api.download_complete_quran(edition)
```

## Data Verification

After setup, verify your data:

```python
from quran_api import QuranAPI

api = QuranAPI()

# Check statistics
stats = api.get_stats()
print(f"Surahs: {stats['total_surahs']}")
print(f"Ayahs: {stats['total_ayahs']}")

# Test random verses
import random
for _ in range(5):
    surah = random.randint(1, 114)
    ayah = random.randint(1, 10)
    verse = api.get_verse(surah, ayah)
    if verse:
        print(f"✅ {surah}:{ayah}")
    else:
        print(f"❌ {surah}:{ayah}")
```

## Performance Tips

### For Faster Access:
- Use SSD storage
- Pre-load common Surahs at startup
- Cache frequently accessed verses

### For Lower Memory:
- Load Surahs on-demand
- Use Simple edition
- Implement verse pagination

## Integration with Flutter

For Flutter integration, create a simple HTTP server:

```python
from flask import Flask, jsonify
from quran_api import QuranAPI

app = Flask(__name__)
api = QuranAPI()

@app.route('/verse/<int:surah>/<int:ayah>')
def get_verse(surah, ayah):
    verse = api.get_verse(surah, ayah)
    return jsonify({'verse': verse})

@app.route('/search/<query>')
def search_verses(query):
    results = api.search_verses(query)
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Then in Flutter:
```dart
// GET http://localhost:5000/verse/1/1
// GET http://localhost:5000/search/الرحمن
```

## Backup and Sync

### Backup Your Data
```bash
# Create backup
tar -czf quran_data_backup.tar.gz quran_data/

# Restore backup
tar -xzf quran_data_backup.tar.gz
```

### Sync Across Devices
- Copy `quran_data/` folder
- Use cloud storage (Google Drive, Dropbox)
- Git repository for version control

## Updates

To update your Quran data:

```bash
# Re-run setup
python setup_quran_data.py

# Or force re-download
python -c "
from quran_api import QuranAPI
import shutil

# Remove old data
shutil.rmtree('quran_data', ignore_errors=True)

# Download fresh
api = QuranAPI()
api.download_complete_quran()
"
```

## Support

For issues:
1. Check internet connection
2. Verify API endpoints are accessible
3. Try different edition
4. Check disk space (need ~20MB free)
5. Run with verbose logging

## Credits

- **AlQuran.cloud** - Primary API source
- **QuranEnc.com** - Alternative API
- **Tarteel.ai** - Quran AI research
- **Islamic Society of North America** - Text verification