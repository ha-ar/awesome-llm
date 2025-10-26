// lib/main.dart
import 'package:flutter/material.dart';
import 'screens/quran_recitation_screen.dart';

void main() {
  runApp(const QuranRecitationApp());
}

class QuranRecitationApp extends StatelessWidget {
  const QuranRecitationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quran Recitation Analyzer',
      theme: ThemeData(
        primarySwatch: Colors.green,
        useMaterial3: true,
      ),
      home: const QuranRecitationScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}