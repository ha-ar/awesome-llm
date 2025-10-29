# Quran Recitation App

A Flutter application for Quran recitation with Tajweed analysis and mistake detection.

## Features

- 🎤 Audio recording of Quran recitation
- 📝 Automatic transcription (server-based or device-based)
- ✅ Mistake detection and correction
- 🎨 Color-coded feedback for learning
- 📊 Accuracy scoring and Tajweed analysis
- 📱 Cross-platform support (Android, iOS, Desktop)

## Platform Support

### ✅ Android
- Python integration via Chaquopy
- On-device text analysis
- Lightweight and optimized

### ⚠️ iOS
- Requires server-based approach or additional configuration
- Native speech recognition recommended

### ✅ Desktop (Windows/macOS/Linux)
- Full Python integration
- ML model support
- Requires Python installation

## Quick Start

### Prerequisites

1. **Flutter SDK** (3.x or higher)
2. **Android Studio** (for Android development)
3. **Xcode** (for iOS development on macOS)
4. **Python 3.8+** (for desktop platforms)

### Installation

```bash
# Clone the repository
cd quran_transcribe

# Install dependencies
flutter pub get

# Run on your platform
flutter run
```

### Building for Android

```bash
# Debug build
flutter build apk --debug

# Release build
flutter build apk --release
```

**Note:** First build will take longer as Chaquopy downloads Python packages.

## Mobile Setup

For detailed mobile configuration including Python integration with Chaquopy, see:
📖 **[MOBILE_SETUP.md](MOBILE_SETUP.md)**

Topics covered:
- Chaquopy configuration
- Platform channels setup
- Building and deployment
- Troubleshooting

## Project Structure

```
quran_transcribe/
├── lib/
│   ├── main.dart                      # App entry point
│   ├── screens/                       # UI screens
│   │   └── quran_recitation_screen.dart
│   └── services/                      # Business logic
│       └── quran_analysis_service.dart # Python integration
├── android/
│   └── app/
│       ├── build.gradle.kts          # Chaquopy configuration
│       └── src/main/
│           ├── kotlin/               # Native Android code
│           │   └── MainActivity.kt   # Platform channel handler
│           └── python/               # Python modules for mobile
│               ├── quran_core_mobile.py
│               └── requirements.txt
├── assets/
│   ├── python/                       # Python scripts
│   └── quran_data/                   # Quran database
└── pubspec.yaml                      # Flutter dependencies
```

## Configuration

### Android (Chaquopy)
Python packages are configured in `android/app/build.gradle.kts`:
```kotlin
python {
    version = "3.9"
    pip {
        install("flask==3.0.0")
        install("flask-cors==4.0.0")
        install("numpy==1.24.3")
    }
}
```

### Desktop
Requires Python installed with packages:
```bash
pip install flask flask-cors transformers torch librosa soundfile numpy
```

## Usage

### Basic Flow
1. **Record Audio** - Tap microphone to start recording
2. **Get Transcription** - Text appears after recording
3. **Analyze** - App checks for mistakes and Tajweed
4. **Review** - See color-coded feedback and corrections

### Color Coding
- 🟢 **Green** - Correct word
- 🔴 **Red** - Wrong word
- 🟡 **Yellow** - Missing word
- 🟠 **Orange** - Extra word

## Development

### Running Tests
```bash
flutter test
```

### Code Analysis
```bash
flutter analyze
```

### Format Code
```bash
flutter format .
```

## Architecture

### Mobile (Android)
```
Flutter (UI) 
  ↓ Platform Channel
Kotlin (Bridge)
  ↓ Chaquopy
Python (Analysis)
  ↓
SQLite Database
```

### Desktop
```
Flutter (UI)
  ↓ Process.start()
Python Server (HTTP)
  ↓
Analysis Engine
  ↓
SQLite Database
```

## Troubleshooting

### "Python not found" on Mobile
✅ **Solution:** This is normal. Chaquopy bundles Python in the APK automatically.

### Build Errors
```bash
# Clean and rebuild
flutter clean
flutter pub get
cd android && ./gradlew clean
cd .. && flutter build apk
```

### Large APK Size
- Normal due to embedded Python (~20-40MB)
- Use App Bundle for Play Store (handles optimization)
- Consider ABI splits for production

### Performance Issues
- Use background processing for Python calls
- Cache analysis results
- Optimize database queries

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Chaquopy Documentation](https://chaquo.com/chaquopy/)
- [Mobile Setup Guide](MOBILE_SETUP.md)

## License

This project is licensed under the Apache License 2.0.

## Acknowledgments

- Quran API for verse data
- Whisper model for Arabic transcription
- Chaquopy for Python on Android

---

For detailed mobile setup and configuration, see **[MOBILE_SETUP.md](MOBILE_SETUP.md)**
