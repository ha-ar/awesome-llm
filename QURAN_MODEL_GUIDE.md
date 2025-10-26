# Quran Recitation Model Guide

## Model Information

### **deepdml/whisper-large-v3-turbo-ar-quran-mix**

This is a **specialized Whisper model fine-tuned specifically for Quran recitation**. 

#### Key Features:
- ✅ **Base Model:** OpenAI Whisper Large V3 Turbo
- ✅ **Fine-tuned on Quran datasets:**
  - `tarteel-ai/everyayah` (127k samples)
  - `tarteel-ai/EA-UD` (4.9k samples)
- ✅ **WER (Word Error Rate):** 13.11% on Common Voice 17.0 (Arabic)
- ✅ **License:** Apache 2.0 (free for commercial use)
- ✅ **Model Size:** 809M parameters

#### Why This Model is Better for Quran:
1. **Trained on actual Quran recitations** from professional Qaris
2. **Understands Tajweed rules** and Quranic pronunciation patterns
3. **Better at Classical Arabic** vs modern spoken Arabic
4. **Handles different recitation styles** (Hafs, Warsh, etc.)
5. **Optimized for religious context** and Quranic vocabulary

## Alternative Models for Quran Recognition

If you want to try other options:

### 1. **tarteel-ai/whisper-base-ar-quran** (Smaller, Faster)
```python
model_id = "tarteel-ai/whisper-base-ar-quran"
```
- Faster inference
- Lower accuracy but still good for Quran
- Better for real-time on CPU

### 2. **tarteel-ai/whisper-small-ar** (Balanced)
```python
model_id = "tarteel-ai/whisper-small-ar"
```
- Good balance of speed and accuracy
- General Arabic + Quran support

### 3. **openai/whisper-large-v3** (General Arabic)
```python
model_id = "openai/whisper-large-v3"
```
- Not Quran-specific but very accurate for all Arabic
- Larger model, more resources needed

### 4. **Faster Alternative: faster-whisper with larger model**
If you need speed but still want reasonable accuracy:
```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
```
- Much faster inference
- Not Quran-specific but decent Arabic support
- Lower memory usage

## Installation

### Required Packages:
```bash
pip install transformers torch accelerate gradio scipy numpy soundfile mishkal safetensors
```

### GPU Support (Recommended):
```bash
# For NVIDIA GPU (much faster)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### CPU Only:
The current setup works on CPU but will be slower. For CPU-only use:
```bash
pip install torch torchvision torchaudio
```

## Performance Optimization

### For GPU (Fastest):
```python
device = "cuda:0"
torch_dtype = torch.float16  # Half precision for speed
```

### For CPU (Slower but works):
```python
device = "cpu"
torch_dtype = torch.float32  # Full precision for compatibility
```

### For Apple Silicon (M1/M2/M3):
```python
device = "mps"  # Metal Performance Shaders
torch_dtype = torch.float16
```

## Expected Performance

### GPU (NVIDIA RTX 3060 or better):
- First load: 10-30 seconds
- Transcription: ~0.5-1 second per audio chunk
- Real-time capable: ✅ Yes

### CPU (Modern Intel/AMD):
- First load: 30-60 seconds
- Transcription: 2-5 seconds per audio chunk
- Real-time capable: ⚠️ Marginally (may lag behind)

### Mobile (Android/iOS):
- Not recommended to run locally
- Use cloud deployment instead

## Switching Models

To switch to a different model, edit line 19 in `app.py`:

```python
model_id = "deepdml/whisper-large-v3-turbo-ar-quran-mix"  # Current
# model_id = "tarteel-ai/whisper-base-ar-quran"  # Smaller, faster
# model_id = "tarteel-ai/whisper-small-ar"  # Balanced
```

## Troubleshooting

### Model Download Issues:
If the model fails to download:
```bash
# Pre-download the model
huggingface-cli download deepdml/whisper-large-v3-turbo-ar-quran-mix
```

### Out of Memory:
If you get OOM errors:
1. Use a smaller model (tarteel-ai/whisper-base-ar-quran)
2. Use CPU instead of GPU
3. Reduce chunk size in app.py

### Slow Transcription:
1. Use GPU if available
2. Switch to faster-whisper (less accurate for Quran)
3. Reduce audio chunk size

## Diacritization (Tashkeel)

The model already outputs some diacritics, but we also use Mishkal for additional diacritization.

To disable Mishkal (faster but less diacritics):
```python
# In transcribe_streaming_audio function, replace:
diacritized_text = tashkeel_instance.tashkeel(new_transcription)
# With:
diacritized_text = new_transcription
```

## Comparison Table

| Model | Size | Speed | Quran Accuracy | General Arabic |
|-------|------|-------|----------------|----------------|
| deepdml/whisper-large-v3-turbo-ar-quran-mix | 809M | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| tarteel-ai/whisper-base-ar-quran | ~150M | Fast | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| openai/whisper-large-v3 | 1550M | Slow | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| faster-whisper (large-v3) | 1550M | Very Fast | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Recommended Setup

### For Best Quran Accuracy (Current):
- Model: `deepdml/whisper-large-v3-turbo-ar-quran-mix`
- Device: GPU (CUDA)
- Precision: float16

### For Best Speed:
- Model: `tarteel-ai/whisper-base-ar-quran`
- Device: GPU (CUDA)
- Precision: float16

### For CPU Users:
- Model: `tarteel-ai/whisper-base-ar-quran`
- Device: CPU
- Precision: float32

## References

- Model: https://huggingface.co/deepdml/whisper-large-v3-turbo-ar-quran-mix
- Tarteel AI: https://www.tarteel.ai/
- Quran Datasets: https://huggingface.co/datasets/tarteel-ai/everyayah
