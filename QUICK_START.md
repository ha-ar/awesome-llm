# 🎯 Quick Start Guide - Quran Mistake Detection

## What You Have Now

A complete Quran recitation learning system with:

1. ✅ **Real-time transcription** using Quran-specific AI model
2. ✅ **Mistake detection** that highlights errors
3. ✅ **Color-coded feedback** for easy learning
4. ✅ **Accuracy scoring** to track progress

## Installation Steps

### 1. Install Python Packages

```bash
# Install all required dependencies
pip install transformers torch accelerate gradio scipy numpy soundfile mishkal safetensors python-bidi arabic-reshaper requests
```

**OR** use the requirements file:

```bash
pip install -r requirements.txt
```

### 2. Download Full Quran Database (Optional but Recommended)

```bash
python setup_quran_db.py
```

This downloads all 114 surahs (~6,236 verses) from the Quran API.

### 3. Run the Application

```bash
python app.py
```

The app will open in your browser at `http://localhost:7860`

## How to Use

### Basic Workflow:

1. **Click "Start Audio Input"** 🎤
   - Allow microphone access when prompted
   - Green waveform shows audio is being captured

2. **Recite a Quran Verse** 📖
   - Speak clearly into your microphone
   - Watch transcription appear in real-time
   - Example: Recite "Bismillah ir-Rahman ir-Raheem"

3. **Check for Mistakes** ✅
   - Click "Check for Mistakes" button
   - (Optional) Enter verse reference like "1:1"
   - View color-coded results

4. **Review Feedback** 📊
   - **Green words** = Correct ✅
   - **Red words** = Wrong (hover to see correction) ❌
   - **Yellow words** = Missing ⚠️
   - **Orange words** = Extra 🔸
   - Check accuracy score and detailed report

5. **Clear and Try Again** 🔄
   - Click "Clear All" to reset
   - Practice the verse again
   - Track your improvement

## Example Session

### Test with Al-Fatiha (1:1):

**Verse 1:1:**
```
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
```

**Steps:**
1. Start recording
2. Recite: "Bismillah ir-Rahman ir-Raheem"
3. Stop recording (transcription appears)
4. Enter "1:1" in Expected Verse field
5. Click "Check for Mistakes"
6. See results!

### Expected Output:
- **100% accuracy** if recited perfectly
- **Color-coded text** showing any mistakes
- **Detailed report** listing each error

## File Structure

```
live-transcribe-ar/
├── app.py                          # Main application
├── quran_checker.py                # Mistake detection engine
├── setup_quran_db.py               # Database download tool
├── requirements.txt                # Dependencies
│
├── USER_GUIDE.md                   # Detailed user guide
├── MISTAKE_DETECTION_GUIDE.md      # How detection works
├── QURAN_MODEL_GUIDE.md            # Model information
├── IMPLEMENTATION_SUMMARY.md       # Technical details
└── quran_data.json                 # Full Quran (created by setup)
```

## Troubleshooting

### 1. Model Not Loading

**Error:** "Failed to load Whisper model"

**Solution:**
```bash
# Install PyTorch first
pip install torch

# Then install transformers
pip install transformers>=4.42.0
```

### 2. No Matching Verse Found

**Error:** "Could not find matching verse"

**Solutions:**
- Run `python setup_quran_db.py` to download full database
- Manually specify verse reference (e.g., "1:1")
- Ensure you're reciting a complete verse

### 3. Dependencies Missing

**Error:** Import errors for "arabic_reshaper" or "bidi"

**Solution:**
```bash
pip install python-bidi arabic-reshaper
```

### 4. Poor Transcription Quality

**Solutions:**
- Use a better quality microphone
- Reduce background noise
- Speak more clearly
- Check microphone permissions in browser

### 5. Slow Performance

**For CPU Users:**
```python
# In app.py, line 13, switch to smaller model:
model_id = "tarteel-ai/whisper-base-ar-quran"
```

**For GPU Users:**
```bash
# Install CUDA version of PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Configuration Options

### Change Model (app.py line 13):

```python
# Current (best for Quran)
model_id = "deepdml/whisper-large-v3-turbo-ar-quran-mix"

# Faster (smaller)
model_id = "tarteel-ai/whisper-base-ar-quran"

# Most accurate (larger)
model_id = "openai/whisper-large-v3"
```

### Adjust Chunk Size (app.py):

```python
# For faster response (less accurate)
min_audio_length_seconds = 0.3

# For better accuracy (slower)
min_audio_length_seconds = 1.0
```

## Best Practices

### For Best Results:

✅ **Do:**
- Use a quiet environment
- Speak clearly at moderate pace
- Recite complete verses
- Use quality microphone
- Specify verse reference when known

❌ **Avoid:**
- Noisy environments
- Speaking too fast or too slow
- Incomplete verses
- Poor quality microphone
- Background music or talking

### For Learning:

1. **Start Simple**: Begin with short surahs (Al-Fatiha, Al-Ikhlas)
2. **Practice Regularly**: Repeat same verse multiple times
3. **Track Progress**: Note your accuracy scores
4. **Focus on Mistakes**: Review highlighted errors
5. **Improve Gradually**: Move to longer verses as you improve

## Verse Reference Guide

Format: `surah:ayah`

**Common Verses:**
- `1:1` = Bismillah (Al-Fatiha, verse 1)
- `1:2` = Alhamdulillah (Al-Fatiha, verse 2)
- `2:255` = Ayat al-Kursi
- `112:1` = Qul Huwa Allahu Ahad (Al-Ikhlas)
- `113:1` = Qul A'udhu bi-Rabbi al-Falaq (Al-Falaq)
- `114:1` = Qul A'udhu bi-Rabbi an-Nas (An-Nas)

## Next Steps

### 1. Immediate:
- ✅ Install dependencies
- ✅ Run setup script
- ✅ Test with Al-Fatiha

### 2. Short-term:
- 📚 Practice daily with different surahs
- 📊 Track your accuracy over time
- 🎯 Focus on verses you struggle with

### 3. Long-term:
- 🌟 Memorize with confidence using feedback
- 📈 Improve pronunciation systematically
- 🎓 Master Tajweed rules

## Getting Help

### Documentation:
1. **USER_GUIDE.md** - Complete usage guide
2. **MISTAKE_DETECTION_GUIDE.md** - How detection works
3. **QURAN_MODEL_GUIDE.md** - Model details

### Common Issues:
- Check Troubleshooting section above
- Review error messages carefully
- Ensure all dependencies are installed

## Summary

You now have a complete system to:
- 🎤 Record Quran recitation
- 📝 Get real-time transcription  
- ✅ Check for mistakes automatically
- 🎨 See visual feedback with colors
- 📊 Track accuracy percentage
- 📋 Review detailed error reports

**Start learning and improving your Quran recitation today!**

---

**Questions or Issues?**
Check the documentation files or review the code comments for detailed information.

**May Allah make it easy for you in your Quran learning journey! 🤲**
