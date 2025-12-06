import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';

// Conditional import to handle dart:io vs web
// We can't import dart:io on web, so we need to be careful.
// Since we can't easily do conditional imports without creating multiple files in this environment,
// we will assume a strategy that avoids direct dart:io usage that breaks web,
// OR use 'universal_io' if we added it. But we didn't add universal_io.
//
// Simple workaround for this specific file:
// We only used Platform.isAndroid and file.path.
// On web file.path is null anyway.
// We can try to detect platform without dart:io using kIsWeb, but for isAndroid we need dart:io.
//
// To make it web-safe without external packages, we can't import dart:io at all if we want it to compile on web.
// But we want Android support too.
//
// The best approach here without adding more packages is to remove the Platform check
// and just default to localhost, or use a config file.
// However, the reviewer mentioned universal_io.
// I will just use kIsWeb and not import dart:io, effectively making "isAndroid" check impossible
// without dart:io. But for Android Emulator `10.0.2.2` is needed.
//
// Let's use a dynamic import approach or just simplify.
// I will comment out dart:io and the android check for now to ensure it works on Web/Desktop (localhost).
// If the user runs on Android, they might need to change the IP manually.
//
// WAIT: I can add 'universal_io' to pubspec.yaml. That is the cleanest way.

import 'package:universal_io/io.dart';

class ApiService {
  // Use localhost for Android emulator (10.0.2.2) or actual localhost for web/desktop
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000';
    try {
      if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    } catch (e) {
      // Platform check failed or not available
    }
    return 'http://localhost:8000';
  }

  static String get wsUrl {
    if (kIsWeb) return 'ws://localhost:8000';
    try {
      if (Platform.isAndroid) return 'ws://10.0.2.2:8000';
    } catch (e) {
      // Platform check failed
    }
    return 'ws://localhost:8000';
  }

  Future<Map<String, dynamic>> uploadZip(PlatformFile file) async {
    var uri = Uri.parse('$baseUrl/upload');
    var request = http.MultipartRequest('POST', uri);

    if (kIsWeb) {
      if (file.bytes != null) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            file.bytes!,
            filename: file.name,
          ),
        );
      }
    } else {
       if (file.path != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'file',
            file.path!,
          ),
        );
       } else if (file.bytes != null) {
         // Fallback if path is null on desktop for some reason
         request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            file.bytes!,
            filename: file.name,
          ),
        );
       }
    }

    try {
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Upload failed: ${response.statusCode} ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  WebSocketChannel connectToWs(String sessionId) {
    return WebSocketChannel.connect(Uri.parse('$wsUrl/ws/$sessionId'));
  }
}
