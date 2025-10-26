// lib/screens/quran_recitation_screen.dart
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_html/flutter_html.dart';
import '../services/quran_analysis_service.dart';
import 'dart:io';

class QuranRecitationScreen extends StatefulWidget {
  const QuranRecitationScreen({super.key});

  @override
  _QuranRecitationScreenState createState() => _QuranRecitationScreenState();
}

class _QuranRecitationScreenState extends State<QuranRecitationScreen> {
  final AudioRecorder _audioRecorder = AudioRecorder();

  bool _isInitialized = false;
  bool _isRecording = false;
  bool _isAnalyzing = false;
  String? _audioPath;
  QuranAnalysisResult? _result;
  String _initializationStatus = 'Initializing...';

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  Future<void> _initializeService() async {
    try {
      setState(() {
        _initializationStatus = 'Requesting permissions...';
      });

      // Request permissions
      await Permission.microphone.request();

      setState(() {
        _initializationStatus = 'Starting Python server...';
      });

      // Initialize service
      bool success = await QuranAnalysisService.initialize();

      setState(() {
        _isInitialized = success;
        _initializationStatus = success ? 'Ready!' : 'Initialization failed';
      });

      if (success) {
        _showSnackBar('🎉 Quran Analyzer Ready!', Colors.green);
      } else {
        _showSnackBar('❌ Initialization failed', Colors.red);
      }

    } catch (e) {
      setState(() {
        _isInitialized = false;
        _initializationStatus = 'Error: $e';
      });
      _showSnackBar('❌ Error: $e', Colors.red);
    }
  }

  Future<void> _startRecording() async {
    if (!_isInitialized) return;

    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        final path = '${directory.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';

        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000),
          path: path,
        );

        setState(() {
          _isRecording = true;
          _audioPath = path;
          _result = null;
        });

        _showSnackBar('🎤 Recording started', Colors.blue);
      }
    } catch (e) {
      _showSnackBar('Recording failed: $e', Colors.red);
    }
  }

  Future<void> _stopRecording() async {
    try {
      await _audioRecorder.stop();

      setState(() {
        _isRecording = false;
        _isAnalyzing = true;
      });

      _showSnackBar('🔄 Analyzing...', Colors.orange);

      if (_audioPath != null) {
        await _analyzeRecording();
      }

    } catch (e) {
      setState(() {
        _isRecording = false;
        _isAnalyzing = false;
      });
      _showSnackBar('Stop recording failed: $e', Colors.red);
    }
  }

  Future<void> _analyzeRecording() async {
    if (_audioPath == null) return;

    try {
      final stopwatch = Stopwatch()..start();

      QuranAnalysisResult result = await QuranAnalysisService.analyzeAudio(_audioPath!);

      stopwatch.stop();

      setState(() {
        _result = result;
        _isAnalyzing = false;
      });

      if (result.hasError) {
        _showSnackBar('❌ Analysis error: ${result.error}', Colors.red);
      } else {
        _showSnackBar(
            '✅ Analysis complete in ${stopwatch.elapsedMilliseconds}ms',
            Colors.green
        );
      }

      // Clean up audio file
      try {
        File(_audioPath!).delete();
      } catch (e) {
        print('Could not delete temp file: $e');
      }

    } catch (e) {
      setState(() {
        _isAnalyzing = false;
      });
      _showSnackBar('Analysis failed: $e', Colors.red);
    }
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🕌 Quran Recitation'),
        backgroundColor: Colors.green[700],
        foregroundColor: Colors.white,
        actions: [
          if (_isInitialized)
            const Icon(Icons.check_circle, color: Colors.white)
          else
            Container(
              width: 20,
              height: 20,
              margin: const EdgeInsets.only(right: 16),
              child: const CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2,
              ),
            ),
        ],
      ),
      body: !_isInitialized
          ? _buildInitializationScreen()
          : _buildMainContent(),
    );
  }

  Widget _buildInitializationScreen() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 24),
            Text(
              'Setting up Quran Analyzer',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              _initializationStatus,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            if (_initializationStatus.contains('failed') || _initializationStatus.contains('Error'))
              ElevatedButton(
                onPressed: _initializeService,
                child: const Text('Retry'),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainContent() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Recording Controls
          Card(
            elevation: 6,
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  Icon(
                    _isRecording ? Icons.mic : Icons.mic_none,
                    size: 64,
                    color: _isRecording ? Colors.red : Colors.green,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _isRecording ? '🎤 Recording...' :
                    _isAnalyzing ? '🔄 Analyzing...' : '🎯 Ready',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton.icon(
                        onPressed: _isRecording || _isAnalyzing ? null : _startRecording,
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Start'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: _isRecording ? _stopRecording : null,
                        icon: const Icon(Icons.stop),
                        label: const Text('Analyze'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        ),
                      ),
                    ],
                  ),

                  if (_isAnalyzing) ...[
                    const SizedBox(height: 20),
                    const LinearProgressIndicator(),
                    const SizedBox(height: 8),
                    const Text('Processing with AI...'),
                  ],
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Results
          if (_result != null && _result!.isSuccessful)
            Expanded(child: _buildResults()),
        ],
      ),
    );
  }

  Widget _buildResults() {
    if (_result == null || !_result!.isSuccessful) return Container();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Score Cards
          Row(
            children: [
              Expanded(
                child: _buildScoreCard(
                  'Word Accuracy',
                  _result!.wordAccuracy,
                  Colors.blue,
                  Icons.spellcheck,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildScoreCard(
                  'Tajweed Score',
                  _result!.tajweedScore,
                  Colors.purple,
                  Icons.auto_awesome,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Performance Info
          Card(
            color: Colors.grey[100],
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('⚡ Analysis: ${(_result!.processingTime * 1000).round()}ms'),
                      Text('📖 Verse: ${_result!.verseReference}'),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('❌ Word Mistakes: ${_result!.totalMistakes}'),
                      Text('🎵 Tajweed Issues: ${_result!.tajweedMistakes}'),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Transcription
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Your Recitation:',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.grey[300]!),
                    ),
                    child: Text(
                      _result!.transcription,
                      style: const TextStyle(
                        fontSize: 20,
                        height: 1.6,
                        fontWeight: FontWeight.w500,
                      ),
                      textDirection: TextDirection.rtl,
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Highlighted Analysis
          if (_result!.highlightedText.isNotEmpty) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Mistake Analysis:',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[50],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Html(
                        data: _result!.highlightedText,
                        style: {
                          "body": Style(
                            fontSize: FontSize(18),
                            textAlign: TextAlign.right,
                            direction: TextDirection.rtl,
                          ),
                        },
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '🟢 Green = Correct  🔴 Red = Wrong',
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
            ),
          ],

          // Detailed Mistakes
          if (_result!.mistakeDetails.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'Word Mistakes (${_result!.mistakeDetails.length}):',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            ..._result!.mistakeDetails.map((mistake) => Card(
              margin: const EdgeInsets.symmetric(vertical: 4),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.red[100],
                  child: Text('${mistake.position + 1}'),
                ),
                title: Text('Word ${mistake.position + 1}'),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('You said: "${mistake.recited}"'),
                    Text('Correct: "${mistake.correct}"', style: const TextStyle(color: Colors.green)),
                  ],
                ),
              ),
            )),
          ],

          // Tajweed Issues
          if (_result!.tajweedDetails.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'Tajweed Rules (${_result!.tajweedDetails.length}):',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            ..._result!.tajweedDetails.map((tajweed) => Card(
              margin: const EdgeInsets.symmetric(vertical: 4),
              child: ListTile(
                leading: Icon(
                  Icons.auto_awesome,
                  color: _getTajweedColor(tajweed.severity),
                ),
                title: Text(tajweed.rule),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Word: "${tajweed.word}"'),
                    Text(tajweed.description, style: const TextStyle(fontSize: 12)),
                  ],
                ),
                trailing: Chip(
                  label: Text(tajweed.severity.toUpperCase()),
                  backgroundColor: _getTajweedColor(tajweed.severity).withOpacity(0.1),
                ),
              ),
            )),
          ],

          const SizedBox(height: 32), // Bottom padding
        ],
      ),
    );
  }

  Widget _buildScoreCard(String title, double score, Color color, IconData icon) {
    return Card(
      elevation: 4,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [color.withOpacity(0.1), color.withOpacity(0.05)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 36),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              '${score.toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 90) return Colors.green;
    if (score >= 75) return Colors.orange;
    return Colors.red;
  }

  Color _getTajweedColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'major': return Colors.red;
      case 'minor': return Colors.orange;
      default: return Colors.grey;
    }
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    QuranAnalysisService.dispose();
    super.dispose();
  }
}