import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import '../services/api_service.dart';
import '../theme.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();
  String? _sessionId;
  WebSocketChannel? _channel;
  final TextEditingController _cmdController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  final List<Map<String, String>> _logs = [];
  bool _isUploading = false;
  String _status = "READY";
  double _progress = 0.0;

  // Model info from messages
  String? _modelName;
  String? _latency;

  @override
  void dispose() {
    _channel?.sink.close();
    _cmdController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _addLog(String text, {String type = 'result'}) {
    setState(() {
      _logs.add({'text': text, 'type': type});
    });
    // Scroll to bottom
    WidgetsBinding.instance.addPostFrameCallback((_) {
       if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _pickAndUploadFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['zip'],
      );

      if (result != null) {
        setState(() {
          _isUploading = true;
          _status = "UPLOADING...";
          _progress = 0.3;
        });

        PlatformFile file = result.files.first;
        _addLog("Uploading ${file.name}...", type: 'progress');

        final response = await _apiService.uploadZip(file);

        setState(() {
          _sessionId = response['session_id'];
          _isUploading = false;
          _status = "CONNECTED";
          _progress = 1.0;
        });

        _addLog("Session created: $_sessionId", type: 'progress');
        _initWebSocket();

        // Auto-hide progress after a delay
        Future.delayed(const Duration(seconds: 1), () {
            if (mounted) setState(() => _progress = 0.0);
        });

      } else {
        // User canceled
      }
    } catch (e) {
      setState(() {
        _isUploading = false;
        _status = "ERROR";
        _progress = 0.0;
      });
      _addLog(e.toString(), type: 'error');
    }
  }

  void _initWebSocket() {
    if (_sessionId == null) return;

    if (_channel != null) {
      _channel!.sink.close();
    }

    _channel = _apiService.connectToWs(_sessionId!);

    _channel!.stream.listen((message) {
      if (!mounted) return;
      try {
        final data = json.decode(message);

        if (data['type'] == 'progress') {
           setState(() {
             _status = data['content'].toString().toUpperCase();
             _progress = 0.6; // Indeterminate mostly
           });
        } else if (data['type'] == 'result') {
           setState(() {
             _status = "READY";
             _progress = 0.0;
             if (data['meta'] != null) {
               _modelName = data['meta']['model'];
               _latency = data['meta']['duration'];
             }
           });
           _addLog(data['content'], type: 'result');
        } else if (data['type'] == 'error') {
           setState(() {
             _status = "ERROR";
             _progress = 0.0;
           });
           _addLog(data['content'], type: 'error');
        }
      } catch (e) {
        _addLog("Raw: $message", type: 'result');
      }
    }, onError: (error) {
      if (mounted) {
        _addLog("WS Error: $error", type: 'error');
        setState(() => _status = "DISCONNECTED");
      }
    }, onDone: () {
      if (mounted) {
        _addLog("WS Closed", type: 'error');
        setState(() => _status = "DISCONNECTED");
      }
    });
  }

  void _sendCommand() {
    if (_sessionId == null) {
      _addLog("Upload a project first!", type: 'error');
      return;
    }
    final cmd = _cmdController.text.trim();
    if (cmd.isEmpty) return;

    _addLog(cmd, type: 'user');
    _channel?.sink.add(cmd);
    _cmdController.clear();
    setState(() {
      _status = "PROCESSING...";
      _progress = 0.2;
    });
  }

  void _sendAutoFix() {
     if (_sessionId == null) return;
     _addLog("Run Auto-Fix", type: 'user');
     _channel?.sink.add("Przeprowadź pełną analizę i naprawę projektu.");
     setState(() {
       _status = "AUTO-FIXING...";
       _progress = 0.2;
     });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Scanlines effect (simplified overlay)
          IgnorePointer(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.1),
                  ],
                  stops: const [0.5, 0.5],
                  tileMode: TileMode.repeated,
                ),
              ),
            ),
          ),

          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // HEADER PANEL
                  Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: CyberTheme.green),
                      color: CyberTheme.black,
                    ),
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              "🤖 RegisLite 6.0 | OmniTool System",
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                shadows: [
                                  const Shadow(color: CyberTheme.green, blurRadius: 4),
                                ],
                              ),
                            ),
                            if (_sessionId != null)
                               Text("ID: $_sessionId", style: const TextStyle(fontSize: 12, color: CyberTheme.dimGreen)),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                _sessionId == null
                                  ? "No target file loaded."
                                  : "Target loaded.",
                                style: const TextStyle(fontSize: 12),
                              ),
                            ),
                            const SizedBox(width: 8),
                            ElevatedButton(
                              onPressed: _isUploading ? null : _pickAndUploadFile,
                              child: Text(_isUploading ? "UPLOADING..." : "UPLOAD ZIP"),
                            ),
                            const SizedBox(width: 8),
                            OutlinedButton(
                              onPressed: _sessionId != null ? _sendAutoFix : null,
                              style: _sessionId == null
                                ? OutlinedButton.styleFrom(side: const BorderSide(color: CyberTheme.dimGreen), foregroundColor: CyberTheme.dimGreen)
                                : null,
                              child: const Text("🔧 AUTO-FIX"),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // MAIN TERMINAL PANEL
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: CyberTheme.green),
                        color: CyberTheme.black,
                      ),
                      child: Column(
                        children: [
                          // Panel Header
                          Container(
                            color: CyberTheme.green,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: const [
                                Text("Terminal & Chat // Memory Enabled", style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 12)),
                                Text("Markdown Supported", style: TextStyle(color: Colors.black, fontSize: 10)),
                              ],
                            ),
                          ),

                          // Meta Bar
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: const BoxDecoration(
                              border: Border(bottom: BorderSide(color: CyberTheme.dimGreen)),
                            ),
                            child: Row(
                              children: [
                                const Text("STATUS: ", style: TextStyle(color: CyberTheme.dimGreen, fontSize: 12)),
                                Text(_status, style: const TextStyle(color: CyberTheme.green, fontSize: 12, shadows: [Shadow(color: CyberTheme.green, blurRadius: 2)])),
                                if (_modelName != null) ...[
                                   const SizedBox(width: 16),
                                   const Text("MODEL: ", style: TextStyle(color: CyberTheme.dimGreen, fontSize: 12)),
                                   Text(_modelName!, style: const TextStyle(color: CyberTheme.amber, fontSize: 12)),
                                ],
                                if (_latency != null) ...[
                                   const SizedBox(width: 16),
                                   const Text("LATENCY: ", style: TextStyle(color: CyberTheme.dimGreen, fontSize: 12)),
                                   Text(_latency!, style: const TextStyle(color: CyberTheme.green, fontSize: 12)),
                                ]
                              ],
                            ),
                          ),

                          // Progress Bar
                          if (_progress > 0)
                            LinearProgressIndicator(
                              value: _progress == 0.6 ? null : _progress, // Indeterminate if 0.6
                              backgroundColor: CyberTheme.dimGreen,
                              color: CyberTheme.green,
                              minHeight: 2,
                            ),

                          // Output Area
                          Expanded(
                            child: ListView.builder(
                              controller: _scrollController,
                              padding: const EdgeInsets.all(12),
                              itemCount: _logs.length,
                              itemBuilder: (context, index) {
                                final log = _logs[index];
                                final type = log['type'];

                                if (type == 'user') {
                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 8),
                                    padding: const EdgeInsets.only(left: 8),
                                    decoration: const BoxDecoration(
                                      border: Border(left: BorderSide(color: CyberTheme.green, width: 2)),
                                    ),
                                    child: Text("> ${log['text']}", style: const TextStyle(fontWeight: FontWeight.bold)),
                                  );
                                } else if (type == 'error') {
                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 8),
                                    padding: const EdgeInsets.only(left: 8),
                                    decoration: const BoxDecoration(
                                      border: Border(left: BorderSide(color: CyberTheme.alert, width: 2)),
                                    ),
                                    child: Text("[ERROR] ${log['text']}", style: const TextStyle(color: CyberTheme.alert)),
                                  );
                                } else if (type == 'progress') {
                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 8.0),
                                    child: Text(">> ${log['text']}", style: const TextStyle(color: CyberTheme.dimGreen, fontStyle: FontStyle.italic, fontSize: 12)),
                                  );
                                } else {
                                  // Result Markdown
                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 16),
                                    padding: const EdgeInsets.only(bottom: 16),
                                    decoration: const BoxDecoration(
                                      border: Border(bottom: BorderSide(color: CyberTheme.dimGreen, width: 0.5)),
                                    ),
                                    child: MarkdownBody(
                                      data: log['text']!,
                                      styleSheet: MarkdownStyleSheet(
                                        p: const TextStyle(color: CyberTheme.green, fontFamily: 'monospace'),
                                        code: const TextStyle(color: CyberTheme.green, backgroundColor: Colors.transparent, fontFamily: 'monospace'),
                                        codeblockDecoration: BoxDecoration(
                                          color: Colors.black,
                                          border: Border.all(color: CyberTheme.dimGreen),
                                        ),
                                      ),
                                    ),
                                  );
                                }
                              },
                            ),
                          ),

                          // Command Input
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: const BoxDecoration(
                              border: Border(top: BorderSide(color: CyberTheme.green)),
                              color: Colors.black,
                            ),
                            child: Row(
                              children: [
                                const Text(">", style: TextStyle(color: CyberTheme.green)),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: TextField(
                                    controller: _cmdController,
                                    decoration: const InputDecoration(
                                      hintText: "Wpisz komendę lub zapytaj AI...",
                                      border: InputBorder.none,
                                      focusedBorder: InputBorder.none,
                                      enabledBorder: InputBorder.none,
                                      contentPadding: EdgeInsets.zero,
                                    ),
                                    style: const TextStyle(color: CyberTheme.green, fontFamily: 'monospace'),
                                    onSubmitted: (_) => _sendCommand(),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
