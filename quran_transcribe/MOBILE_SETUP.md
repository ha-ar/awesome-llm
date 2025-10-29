# Mobile Setup Guide - Quran Recitation App

## Overview

This Flutter app now supports running Python code on Android devices using **Chaquopy**, a Python SDK for Android. This enables the Quran analysis features to work directly on mobile devices.

## Architecture

### Desktop Platforms (Windows/macOS/Linux)
- Uses `Process.start()` to run Python as a subprocess
- Requires Python to be installed on the system
- Full features including ML model loading

### Mobile Platforms (Android)
- Uses **Chaquopy** to embed Python in the Android app
- Python code runs natively in the Android environment
- Lightweight version without heavy ML dependencies
- Platform channels bridge Flutter ↔ Kotlin ↔ Python

### iOS Support
- iOS support would require a different approach (e.g., Kivy for iOS or server-based)
- Currently, iOS falls back to platform channel but needs additional configuration
- Recommended: Use server-based approach for iOS

## Android Setup with Chaquopy

### Prerequisites

1. **Android Studio** installed
2. **Flutter SDK** installed
3. **Android SDK** with minimum API level 21
4. **Internet connection** for Chaquopy to download Python packages

### Configuration Files Modified

#### 1. `android/build.gradle.kts`
Added Chaquopy repository and classpath:
```kotlin
buildscript {
    dependencies {
        classpath("com.chaquo.python:gradle:15.0.1")
    }
}
```

#### 2. `android/app/build.gradle.kts`
- Added Chaquopy plugin
- Set minimum SDK to 21 (Chaquopy requirement)
- Configured Python version and packages:
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

#### 3. Python Files Location
Python files are placed in: `android/app/src/main/python/`
- `quran_core_mobile.py` - Lightweight analysis module
- `requirements.txt` - Python package dependencies

#### 4. Native Bridge: `MainActivity.kt`
Implements platform channels to communicate between Flutter and Python:
- `initializePython` - Initialize Chaquopy Python environment
- `startPythonServer` - Start Flask server (if needed)
- `analyzeText` - Analyze pre-transcribed text
- `getVerse` - Retrieve verse from database

#### 5. Flutter Service: `quran_analysis_service.dart`
Updated to:
- Detect platform (mobile vs desktop)
- Use platform channels on Android/iOS
- Use Process.start() on desktop platforms
- Skip Python file copying on mobile (bundled in APK)

## Mobile vs Desktop Differences

### Desktop Version
✅ Full Whisper model loading
✅ Audio transcription on device
✅ All ML features available
⚠️ Requires Python installed

### Mobile Version (Android with Chaquopy)
✅ Python embedded in APK
✅ Database operations
✅ Text analysis and Tajweed checking
✅ No Python installation needed
⚠️ ML models too large (use server for transcription)
⚠️ Lightweight approach recommended

## Building for Android

### 1. Clean and Get Dependencies
```bash
cd quran_transcribe
flutter clean
flutter pub get
```

### 2. Build APK/Bundle
```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# Android App Bundle (for Google Play)
flutter build appbundle --release
```

### 3. First Build Notes
- First build will take longer as Chaquopy downloads Python and packages
- Subsequent builds are faster (packages cached)
- APK size will be larger due to embedded Python (~20-40MB additional)

## Usage Flow on Mobile

### Recommended Approach: Hybrid
1. **Audio Recording** → Done on device (Flutter)
2. **Audio Transcription** → Send to server or use device speech-to-text
3. **Text Analysis** → Done on device (Python via Chaquopy)
4. **Display Results** → Flutter UI

### Code Example
```dart
// Use platform channel for text analysis
const platform = MethodChannel('com.example.quran_transcribe/python');

// Analyze pre-transcribed text
String transcription = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ";
String jsonResult = await platform.invokeMethod('analyzeText', {
  'transcription': transcription,
  'verseRef': '1:1'
});

// Parse JSON result
Map<String, dynamic> result = json.decode(jsonResult);
```

## Troubleshooting

### Build Fails with "Python not found"
**Solution:** Chaquopy will download Python automatically. Ensure:
- Internet connection available during build
- Gradle has proper proxy settings if behind firewall

### APK Size Too Large
**Cause:** Embedded Python and packages add size
**Solutions:**
- Use ABI splits to create separate APKs per architecture
- Remove unused Python packages
- Use App Bundle instead of APK (Play Store handles optimization)

### Platform Channel Not Working
**Check:**
1. Channel name matches in Dart and Kotlin: `com.example.quran_transcribe/python`
2. Methods are properly registered in MainActivity.kt
3. Python module name is correct: `quran_core_mobile`

### Python Import Errors
**Solution:** 
- Verify packages are listed in build.gradle.kts pip section
- Check package versions are compatible with Python 3.9
- Some packages may not be available for Android (check Chaquopy compatibility)

### Runtime Crashes
**Debug:**
```bash
# View Android logs
adb logcat | grep -i python
adb logcat | grep -i flutter
```

## Performance Optimization

### 1. Lazy Loading
- Initialize Python only when needed
- Cache Python analyzer instance
- Reuse database connections

### 2. Background Processing
- Run Python calls in background to avoid UI blocking
- Use Flutter Isolates for heavy operations
- Show loading indicators during analysis

### 3. Database Optimization
- Pre-populate database with common verses
- Use indexes for fast verse lookup
- Keep database file size reasonable

## Alternative Approaches

### Server-Based (Recommended for iOS)
```
Mobile App → HTTP → Backend Server (Python) → Response → Mobile App
```
**Pros:** 
- Works on all platforms
- Can use full ML models
- Centralized updates

**Cons:**
- Requires internet
- Server costs
- Latency

### Speech-to-Text API
Use native speech recognition instead of Whisper:
- Android: `SpeechRecognizer` with Arabic support
- iOS: `SFSpeechRecognizer` with Arabic
- Then use on-device Python for analysis

## Next Steps

1. **Test on Physical Device**
   ```bash
   flutter run --release
   ```

2. **Add Error Handling**
   - Graceful fallbacks if Python fails
   - Clear error messages to users

3. **Optimize Database**
   - Add full Quran verses
   - Implement verse search
   - Cache frequently used verses

4. **Consider Server Hybrid**
   - On-device for basic analysis
   - Server for heavy ML transcription
   - Best of both worlds

## Resources

- [Chaquopy Documentation](https://chaquo.com/chaquopy/doc/current/)
- [Flutter Platform Channels](https://docs.flutter.dev/development/platform-integration/platform-channels)
- [Android Development](https://developer.android.com/)

## Support

For issues specific to:
- **Chaquopy:** Check [Chaquopy GitHub Issues](https://github.com/chaquo/chaquopy/issues)
- **Flutter:** Check [Flutter Documentation](https://docs.flutter.dev/)
- **Python on Mobile:** Consider server-based approach for complex ML operations

---

**Last Updated:** October 2024
**Flutter Version:** 3.x
**Chaquopy Version:** 15.0.1
**Python Version:** 3.9
