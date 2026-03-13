import 'package:flutter/material.dart';
import 'dart:js_util';
import 'package:js/js.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// --- CHROME INTEROP ---
@JS('chrome.tabs.query')
external dynamic queryTabs(dynamic queryInfo);

Future<String?> getActiveTabUrl() async {
  var queryInfo = jsify({'active': true, 'lastFocusedWindow': true});
  var tabs = await promiseToFuture(queryTabs(queryInfo));
  
  if (tabs != null && tabs.length > 0) {
    return getProperty(tabs[0], 'url');
  }
  return null;
}

void main() {
  runApp(const QShieldApp());
}

class QShieldApp extends StatelessWidget {
  const QShieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Q-Shield Quantum Auth',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.cyan,
        useMaterial3: true,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _result = "Ready for Quantum Scan";
  bool _isLoading = false;

  Future<void> startQuantumScan() async {
    setState(() { 
      _isLoading = true; 
      _result = "Accessing Hilbert Space...";
    });

    try {
      // 1. Grab the URL from the browser
      String? currentUrl = await getActiveTabUrl();
      
      if (currentUrl == null) {
        setState(() { 
          _result = "Error: Could not grab tab URL"; 
          _isLoading = false; 
        });
        return;
      }

      // 2. Send it to your Python Backend
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/scan'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'url': currentUrl}),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);
        setState(() {
          _result = data['is_safe'] 
              ? "✅ SAFE\nQuantum Verified" 
              : "🚨 PHISHING DETECTED\nMalicious Pattern Found";
        });
      }
    } catch (e) {
      setState(() { _result = "Connection Error!\nEnsure Python API is running."; });
    } finally {
      setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E21), // High-tech dark blue
      appBar: AppBar(
        title: const Text("Q-SHIELD AI", style: TextStyle(letterSpacing: 2)),
        backgroundColor: const Color(0xFF1D2136),
        centerTitle: true,
      ),
      body: Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Visual Scanner Icon
            Container(
              height: 140,
              width: 140,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: _isLoading ? Colors.cyan : Colors.blueAccent, 
                  width: 3
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.cyan.withOpacity(0.3), 
                    blurRadius: 15, 
                    spreadRadius: 5
                  )
                ],
              ),
              child: Icon(
                _isLoading ? Icons.sync : Icons.security_sharp,
                size: 70,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 40),
            
            // Result Text Box
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                _result,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: _result.contains("🚨") ? Colors.redAccent : Colors.cyanAccent,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 50),
            
            // Action Button
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _isLoading ? null : startQuantumScan,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyan,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: Text(
                  _isLoading ? "QUANTUM PROCESSING..." : "START SCAN",
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}