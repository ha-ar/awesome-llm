package com.example.quran_transcribe

import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.quran_transcribe/python"
    private var pythonServerStarted = false

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "initializePython" -> {
                    try {
                        if (!Python.isStarted()) {
                            Python.start(AndroidPlatform(this))
                        }
                        result.success(true)
                    } catch (e: Exception) {
                        result.error("INIT_ERROR", "Failed to initialize Python: ${e.message}", null)
                    }
                }
                
                "startPythonServer" -> {
                    try {
                        if (!pythonServerStarted) {
                            startPythonServer()
                            pythonServerStarted = true
                        }
                        result.success(true)
                    } catch (e: Exception) {
                        result.error("SERVER_ERROR", "Failed to start server: ${e.message}", null)
                    }
                }
                
                "checkServerHealth" -> {
                    // Server health check would be done via HTTP from Dart side
                    result.success(pythonServerStarted)
                }
                
                "analyzeAudio" -> {
                    val audioPath = call.argument<String>("audioPath")
                    val verseRef = call.argument<String>("verseRef") ?: ""
                    
                    if (audioPath != null) {
                        try {
                            val analysisResult = analyzeAudioWithPython(audioPath, verseRef)
                            result.success(analysisResult)
                        } catch (e: Exception) {
                            result.error("ANALYSIS_ERROR", "Failed to analyze: ${e.message}", null)
                        }
                    } else {
                        result.error("INVALID_ARGUMENT", "Audio path is required", null)
                    }
                }
                
                "analyzeText" -> {
                    val transcription = call.argument<String>("transcription")
                    val verseRef = call.argument<String>("verseRef") ?: ""
                    
                    if (transcription != null) {
                        try {
                            val analysisResult = analyzeTextWithPython(transcription, verseRef)
                            result.success(analysisResult)
                        } catch (e: Exception) {
                            result.error("ANALYSIS_ERROR", "Failed to analyze: ${e.message}", null)
                        }
                    } else {
                        result.error("INVALID_ARGUMENT", "Transcription is required", null)
                    }
                }
                
                "getVerse" -> {
                    val reference = call.argument<String>("reference")
                    
                    if (reference != null) {
                        try {
                            val verseText = getVerseWithPython(reference)
                            result.success(verseText)
                        } catch (e: Exception) {
                            result.error("VERSE_ERROR", "Failed to get verse: ${e.message}", null)
                        }
                    } else {
                        result.error("INVALID_ARGUMENT", "Reference is required", null)
                    }
                }
                
                else -> result.notImplemented()
            }
        }
    }
    
    private fun startPythonServer() {
        val py = Python.getInstance()
        
        // Start server in background thread
        Thread {
            try {
                val serverModule = py.getModule("quran_server")
                serverModule.callAttr("start_server", 5000)
            } catch (e: Exception) {
                android.util.Log.e("PythonServer", "Error starting server: ${e.message}")
            }
        }.start()
    }
    
    private fun analyzeAudioWithPython(audioPath: String, verseRef: String): String {
        val py = Python.getInstance()
        val coreModule = py.getModule("quran_core_mobile")
        
        // Call Python analysis function (returns JSON string)
        val result = coreModule.callAttr("analyze_audio", audioPath, verseRef)
        
        return result.toString()
    }
    
    private fun analyzeTextWithPython(transcription: String, verseRef: String): String {
        val py = Python.getInstance()
        val coreModule = py.getModule("quran_core_mobile")
        
        // Call Python text analysis function (returns JSON string)
        val result = coreModule.callAttr("analyze_text", transcription, verseRef)
        
        return result.toString()
    }
    
    private fun getVerseWithPython(reference: String): String {
        val py = Python.getInstance()
        val coreModule = py.getModule("quran_core_mobile")
        
        // Get verse text (returns JSON string)
        val result = coreModule.callAttr("get_verse_text", reference)
        
        return result.toString()
    }
}
