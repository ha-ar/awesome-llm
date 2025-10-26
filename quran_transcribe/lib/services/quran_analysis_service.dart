// lib/services/quran_analysis_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/services.dart';

class QuranAnalysisService {
  static final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    sendTimeout: const Duration(seconds: 30),
  ));

  static Process? _pythonProcess;
  static bool _serverRunning = false;
  static const int _serverPort = 5000;
  static const String _baseUrl = 'http://127.0.0.1:$_serverPort';

  /// Initialize the service and start Python server
  static Future<bool> initialize() async {
    try {
      print('🔧 Initializing Quran Analysis Service...');

      // Copy Python files to app directory
      await _copyPythonAssets();

      // Start Python server
      bool serverStarted = await _startPythonServer();

      if (serverStarted) {
        // Wait and verify server is responding
        for (int i = 0; i < 10; i++) {
          await Future.delayed(const Duration(seconds: 1));
          if (await _checkServerHealth()) {
            print('✅ Service initialized successfully');
            return true;
          }
        }
      }

      print('❌ Service initialization failed');
      return false;

    } catch (e) {
      print('❌ Initialization error: $e');
      return false;
    }
  }

  /// Copy Python files from assets to app directory
  static Future<void> _copyPythonAssets() async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final pythonDir = Directory('${appDir.path}/python');

      if (!await pythonDir.exists()) {
        await pythonDir.create(recursive: true);
      }

      // List of Python files to copy
      final pythonFiles = [
        'quran_server.py',
        'requirements.txt',
      ];

      for (String fileName in pythonFiles) {
        try {
          final byteData = await rootBundle.load('assets/python/$fileName');
          final file = File('${pythonDir.path}/$fileName');
          await file.writeAsBytes(byteData.buffer.asUint8List());
          print('📄 Copied $fileName');
        } catch (e) {
          print('⚠️ Could not copy $fileName: $e');
        }
      }
    } catch (e) {
      print('❌ Error copying Python assets: $e');
      throw e;
    }
  }

  /// Start Python server as a subprocess
  static Future<bool> _startPythonServer() async {
    if (_serverRunning) return true;

    try {
      final appDir = await getApplicationDocumentsDirectory();
      final pythonDir = '${appDir.path}/python';

      print('🐍 Starting Python server...');

      // Try different Python commands
      List<String> pythonCommands = ['python3', 'python', 'py'];

      for (String pythonCmd in pythonCommands) {
        try {
          _pythonProcess = await Process.start(
            pythonCmd,
            ['quran_server.py'],
            workingDirectory: pythonDir,
            environment: {'PYTHONUNBUFFERED': '1'},
          );

          // Listen to process output
          _pythonProcess!.stdout.transform(utf8.decoder).listen((data) {
            print('Python: $data');
          });

          _pythonProcess!.stderr.transform(utf8.decoder).listen((data) {
            print('Python Error: $data');
          });

          _serverRunning = true;
          print('✅ Python server started with $pythonCmd');
          return true;

        } catch (e) {
          print('⚠️ Failed to start with $pythonCmd: $e');
          continue;
        }
      }

      print('❌ Could not start Python server with any command');
      return false;

    } catch (e) {
      print('❌ Error starting Python server: $e');
      return false;
    }
  }

  /// Check if server is healthy
  static Future<bool> _checkServerHealth() async {
    try {
      final response = await _dio.get('$_baseUrl/health');
      return response.statusCode == 200 && response.data['status'] == 'healthy';
    } catch (e) {
      return false;
    }
  }

  /// Analyze audio file completely
  static Future<QuranAnalysisResult> analyzeAudio(
      String audioPath, {
        String verseRef = "",
      }) async {
    try {
      if (!_serverRunning) {
        throw Exception('Service not initialized');
      }

      print('🎤 Analyzing audio: $audioPath');

      FormData formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(audioPath),
        'verse_ref': verseRef,
      });

      final response = await _dio.post(
        '$_baseUrl/analyze',
        data: formData,
      );

      if (response.statusCode == 200) {
        return QuranAnalysisResult.fromJson(response.data);
      } else {
        throw Exception('Analysis failed: ${response.statusCode}');
      }

    } catch (e) {
      print('❌ Analysis error: $e');
      throw Exception('Analysis failed: $e');
    }
  }

  /// Get specific verse
  static Future<String> getVerse(int surah, int ayah) async {
    try {
      final response = await _dio.get('$_baseUrl/verse/$surah/$ayah');

      if (response.statusCode == 200) {
        return response.data['verse'] ?? '';
      }

      return '';
    } catch (e) {
      print('❌ Get verse error: $e');
      return '';
    }
  }

  /// Stop the service and cleanup
  static Future<void> dispose() async {
    if (_pythonProcess != null) {
      _pythonProcess!.kill();
      _pythonProcess = null;
      _serverRunning = false;
      print('🛑 Python server stopped');
    }
  }
}

// Data models
class QuranAnalysisResult {
  final String transcription;
  final double wordAccuracy;
  final double tajweedScore;
  final int totalMistakes;
  final int tajweedMistakes;
  final String highlightedText;
  final List<MistakeDetail> mistakeDetails;
  final List<TajweedDetail> tajweedDetails;
  final String verseReference;
  final double processingTime;
  final String error;

  QuranAnalysisResult({
    required this.transcription,
    required this.wordAccuracy,
    required this.tajweedScore,
    required this.totalMistakes,
    required this.tajweedMistakes,
    required this.highlightedText,
    required this.mistakeDetails,
    required this.tajweedDetails,
    required this.verseReference,
    required this.processingTime,
    this.error = "",
  });

  factory QuranAnalysisResult.fromJson(Map<String, dynamic> json) {
    return QuranAnalysisResult(
      transcription: json['transcription'] ?? '',
      wordAccuracy: (json['word_accuracy'] ?? 0.0).toDouble(),
      tajweedScore: (json['tajweed_score'] ?? 0.0).toDouble(),
      totalMistakes: json['total_mistakes'] ?? 0,
      tajweedMistakes: json['tajweed_mistakes'] ?? 0,
      highlightedText: json['highlighted_text'] ?? '',
      mistakeDetails: (json['mistake_details'] as List<dynamic>?)
          ?.map((e) => MistakeDetail.fromJson(e))
          .toList() ?? [],
      tajweedDetails: (json['tajweed_details'] as List<dynamic>?)
          ?.map((e) => TajweedDetail.fromJson(e))
          .toList() ?? [],
      verseReference: json['verse_reference'] ?? '',
      processingTime: (json['processing_time'] ?? 0.0).toDouble(),
      error: json['error'] ?? '',
    );
  }

  bool get hasError => error.isNotEmpty;
  bool get isSuccessful => !hasError && transcription.isNotEmpty;
}

class MistakeDetail {
  final int position;
  final String recited;
  final String correct;
  final String type;

  MistakeDetail({
    required this.position,
    required this.recited,
    required this.correct,
    required this.type,
  });

  factory MistakeDetail.fromJson(Map<String, dynamic> json) {
    return MistakeDetail(
      position: json['position'] ?? 0,
      recited: json['recited'] ?? '',
      correct: json['correct'] ?? '',
      type: json['type'] ?? '',
    );
  }
}

class TajweedDetail {
  final String rule;
  final String word;
  final int position;
  final String severity;
  final String description;

  TajweedDetail({
    required this.rule,
    required this.word,
    required this.position,
    required this.severity,
    required this.description,
  });

  factory TajweedDetail.fromJson(Map<String, dynamic> json) {
    return TajweedDetail(
      rule: json['rule'] ?? '',
      word: json['word'] ?? '',
      position: json['position'] ?? 0,
      severity: json['severity'] ?? '',
      description: json['description'] ?? '',
    );
  }
}