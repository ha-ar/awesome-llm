---
title: Live Transcribe Ar
emoji: 🦀
colorFrom: pink
colorTo: pink
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: apache-2.0
---

# Awesome LLM - Quran Recitation & Analysis

A comprehensive system for Quran recitation learning with AI-powered transcription, mistake detection, and Tajweed analysis.

## Components

### 🌐 Web Application (Gradio)
Desktop web interface with real-time transcription and analysis.
- **Location:** Root directory
- **Run:** `python app.py`
- **Guide:** [QUICK_START.md](QUICK_START.md)

### 📱 Mobile Application (Flutter)
Cross-platform mobile app with on-device Python integration.
- **Location:** `quran_transcribe/`
- **Platform:** Android (✅), iOS (⚠️), Desktop (✅)
- **Setup:** [quran_transcribe/MOBILE_SETUP.md](quran_transcribe/MOBILE_SETUP.md)
- **Quick Start:** [quran_transcribe/QUICK_START_MOBILE.md](quran_transcribe/QUICK_START_MOBILE.md)

## Recent Updates

### ✨ Mobile Python Configuration (Latest)
Fixed "Python not found" error on mobile devices by:
- Integrating Chaquopy for Android (Python SDK)
- Creating platform channels for Flutter ↔ Kotlin ↔ Python communication
- Implementing lightweight mobile-optimized Python modules
- Supporting offline operation on Android devices

**See:** [PYTHON_MOBILE_CONFIG_SUMMARY.md](PYTHON_MOBILE_CONFIG_SUMMARY.md)

## Quick Links

### Documentation
- 📖 [User Guide](USER_GUIDE.md)
- 🔧 [Quick Start](QUICK_START.md)
- 📊 [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- 🐛 [Mistake Detection Guide](MISTAKE_DETECTION_GUIDE.md)
- 🤖 [Quran Model Guide](QURAN_MODEL_GUIDE.md)
- 📱 [Mobile Setup](quran_transcribe/MOBILE_SETUP.md)

### Getting Started
- **Web App:** `pip install -r requirements.txt && python app.py`
- **Mobile App:** `cd quran_transcribe && flutter run`

## Features

- 🎤 Real-time audio recording
- 📝 Arabic transcription using Whisper
- ✅ Word-level mistake detection
- 🎨 Color-coded feedback (correct, wrong, missing, extra)
- 📊 Accuracy scoring
- 🕌 Tajweed rule checking
- 📱 Mobile & desktop support
- 🔒 Offline operation (mobile)

## License

Apache License 2.0

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
