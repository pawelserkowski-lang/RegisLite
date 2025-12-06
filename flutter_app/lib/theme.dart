import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class CyberTheme {
  static const Color black = Color(0xFF000000);
  static const Color green = Color(0xFF00FF41);
  static const Color dimGreen = Color(0xFF003B00);
  static const Color alert = Color(0xFFFF0000);
  static const Color amber = Color(0xFFFFB000);

  static ThemeData get themeData {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: black,
      primaryColor: green,
      colorScheme: const ColorScheme.dark(
        primary: green,
        secondary: green,
        background: black,
        surface: black,
        error: alert,
        onPrimary: black,
        onSecondary: black,
        onBackground: green,
        onSurface: green,
        onError: black,
      ),
      fontFamily: GoogleFonts.courierPrime().fontFamily,
      textTheme: TextTheme(
        bodyMedium: TextStyle(color: green, fontFamily: GoogleFonts.courierPrime().fontFamily),
        bodyLarge: TextStyle(color: green, fontFamily: GoogleFonts.courierPrime().fontFamily),
        titleLarge: TextStyle(color: green, fontWeight: FontWeight.bold, fontFamily: GoogleFonts.courierPrime().fontFamily),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(color: dimGreen),
          borderRadius: BorderRadius.zero,
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(color: green),
          borderRadius: BorderRadius.zero,
        ),
        border: OutlineInputBorder(
          borderSide: BorderSide(color: dimGreen),
          borderRadius: BorderRadius.zero,
        ),
        labelStyle: TextStyle(color: green),
        hintStyle: TextStyle(color: dimGreen),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: black,
          foregroundColor: green,
          side: const BorderSide(color: green),
          shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
          textStyle: TextStyle(fontFamily: GoogleFonts.courierPrime().fontFamily, fontWeight: FontWeight.bold),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: green,
          textStyle: TextStyle(fontFamily: GoogleFonts.courierPrime().fontFamily),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: green,
          side: const BorderSide(color: dimGreen),
          shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
          textStyle: TextStyle(fontFamily: GoogleFonts.courierPrime().fontFamily),
        ),
      ),
    );
  }
}
