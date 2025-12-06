import 'package:flutter/material.dart';
import 'theme.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RegisLite 6.0',
      theme: CyberTheme.themeData,
      home: const DashboardScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
