# 🕌 Quran Recitation Live Transcriber & Mistake Checker

An AI-powered tool for real-time Quran recitation transcription with intelligent mistake detection and highlighting.

## ✨ Features

- 🎤 **Real-time Transcription**: Instant speech-to-text as you recite
- 🤖 **Quran-Specific AI Model**: Fine-tuned on 130k+ Quran recitation samples
- ✅ **Mistake Detection**: Identifies wrong, missing, and extra words
- 🎨 **Visual Highlighting**: Color-coded feedback for easy learning
- 📊 **Accuracy Scoring**: Track your recitation accuracy
- 🌐 **Arabic RTL Support**: Proper right-to-left text display
- 📱 **Multi-Device**: Works on laptop, desktop, and mobile browsers

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. **Download Full Quran Database** (Recommended):
```bash
python setup_quran_db.py
```

2. **Run the Application**:
```bash
python app.py
```

3. **Open in Browser**:
- The app will open automatically at `http://localhost:7860`

## 📖 How to Use

### Step 1: Start Recording
1. Click "Start Audio Input"
2. Allow microphone access
3. Begin reciting Quran verses clearly

### Step 2: View Transcription
- Watch real-time transcription appear as you speak
- Text displays with diacritical marks (tashkeel)

### Step 3: Check for Mistakes
1. Click "Check for Mistakes" button
2. Optionally enter verse reference (e.g., "1:1")
3. View highlighted mistakes and detailed report

## 🎨 Color Legend

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 **Green** | Correct word | Keep it up! |
| 🔴 **Red** | Wrong word | Hover to see correct word |
| 🟡 **Yellow** | Missing word | You skipped this word |
| 🟠 **Orange** | Extra word | Remove this word |

## 📊 Understanding Accuracy

- **90-100%**: Excellent! Minor improvements
- **75-89%**: Good, review mistakes
- **60-74%**: Fair, practice more
- **Below 60%**: Needs practice

## 🔧 Configuration

### Using Different Model

Edit `app.py` line 13:

```python
# Current (Quran-specific, recommended)
model_id = "deepdml/whisper-large-v3-turbo-ar-quran-mix"

# Smaller, faster
model_id = "tarteel-ai/whisper-base-ar-quran"

# Larger, more accurate
model_id = "openai/whisper-large-v3"
```

### GPU Acceleration

If you have NVIDIA GPU:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

The app will automatically use GPU if available.

## 📚 Documentation

- [Quran Model Guide](QURAN_MODEL_GUIDE.md) - Model selection and configuration
- [Mistake Detection Guide](MISTAKE_DETECTION_GUIDE.md) - How mistake detection works
- [Optimization Notes](OPTIMIZATION_NOTES.md) - Performance tuning

## 🔍 Verse Reference Format

Use format: `surah:ayah`

Examples:
- `1:1` - Al-Fatiha, verse 1
- `2:255` - Ayat al-Kursi
- `112:1` - Al-Ikhlas, verse 1

## 🛠️ Advanced Features

### Expand Verse Database

#### Option 1: Run Setup Script
```bash
python setup_quran_db.py
```
Downloads all 114 surahs automatically.

#### Option 2: Manual Addition
Edit `quran_checker.py` and add verses:

```python
def _load_quran_sample(self):
    return {
        "1:1": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "2:255": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ...",
        # Add more verses
    }
```

## 🐛 Troubleshooting

### "No matching verse found"
- Specify verse reference manually
- Run `python setup_quran_db.py` to download full database
- Ensure reciting complete verses

### Poor Transcription Quality
- Use better microphone
- Reduce background noise
- Speak clearly and at moderate pace
- Ensure 16kHz sample rate

### Slow Performance
- Use GPU if available
- Switch to smaller model (`tarteel-ai/whisper-base-ar-quran`)
- Reduce chunk size in `app.py`

## 📦 Dependencies

- `gradio` - Web interface
- `transformers` - AI model loading
- `torch` - Deep learning framework
- `mishkal` - Arabic diacritization
- `scipy` - Audio processing
- `python-bidi` - Arabic text rendering
- `requests` - API calls

## 🎯 Best Practices

### For Accurate Detection
✅ Recite complete verses  
✅ Use quality microphone  
✅ Minimize background noise  
✅ Speak clearly at moderate pace  
✅ Specify verse reference when known  

### For Learning
📚 Start with short surahs  
🔁 Practice same verse multiple times  
📊 Track accuracy improvement  
✍️ Note common mistakes  
🎯 Focus on problematic words  

## 📄 License

Apache 2.0

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Base ASR model
- [Tarteel AI](https://www.tarteel.ai/) - Quran recitation datasets
- [DeepDML](https://huggingface.co/deepdml) - Fine-tuned Quran model
- [Al-Quran Cloud](https://alquran.cloud/) - Quran API

---

**Made with ❤️ for Quran learners worldwide**
