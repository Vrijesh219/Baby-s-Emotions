import 'package:flutter/material.dart';

class DashboardPage extends StatefulWidget {
  final Map<String, String> userData;

  const DashboardPage({super.key, required this.userData});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _selectedTabIndex = 0;
  String _selectedLanguage = 'EN';
  String? _selectedFileName;
  double _confidenceThreshold = 50.0;
  bool _isAnalyzing = false;

  final List<String> languages = ['EN', 'HI', 'GU'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF8B5CF6), Color(0xFF7C3AED)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Top Navigation Bar
              _buildTopNavigation(),

              // Main Content
              Expanded(child: _buildMainContent()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopNavigation() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          // Tabs
          Expanded(
            child: Row(
              children: [
                _buildTab('Upload Audio', Icons.upload, 0),
                const SizedBox(width: 8),
                _buildTab('Record Voice', Icons.mic, 1),
                const SizedBox(width: 8),
                _buildTab('History', Icons.history, 2),
              ],
            ),
          ),

          // Profile Icon
          _buildProfileIcon(),
        ],
      ),
    );
  }

  Widget _buildTab(String title, IconData icon, int index) {
    final isSelected = _selectedTabIndex == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedTabIndex = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? Colors.white : Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: isSelected ? const Color(0xFF8B5CF6) : Colors.white,
                size: 20,
              ),
              const SizedBox(width: 4),
              Text(
                title,
                style: TextStyle(
                  color: isSelected ? const Color(0xFF8B5CF6) : Colors.white,
                  fontWeight: FontWeight.w600,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children:
            languages.map((lang) {
              final isSelected = _selectedLanguage == lang;
              return GestureDetector(
                onTap: () => setState(() => _selectedLanguage = lang),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.white : Colors.transparent,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    lang,
                    style: TextStyle(
                      color:
                          isSelected ? const Color(0xFF8B5CF6) : Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              );
            }).toList(),
      ),
    );
  }

  Widget _buildProfileIcon() {
    return GestureDetector(
      onTap: () => _showProfileDialog(),
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: const Icon(Icons.person, color: Color(0xFF8B5CF6), size: 24),
      ),
    );
  }

  Widget _buildMainContent() {
    switch (_selectedTabIndex) {
      case 0:
        return _buildUploadAudioTab();
      case 1:
        return _buildRecordVoiceTab();
      case 2:
        return _buildHistoryTab();
      default:
        return _buildUploadAudioTab();
    }
  }

  Widget _buildUploadAudioTab() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Title
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.upload, color: Color(0xFF8B5CF6), size: 28),
                const SizedBox(width: 8),
                const Text(
                  'Upload Audio File',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2C3E50),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // File Selection
            Row(
              children: [
                const Text(
                  'Select Audio File (WAV, MP3, M4A):',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2C3E50),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _selectedFileName ?? 'No file selected',
                      style: TextStyle(
                        color:
                            _selectedFileName != null
                                ? Colors.black
                                : Colors.grey,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _selectFile,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF8B5CF6),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Choose File'),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Confidence Threshold
            Row(
              children: [
                const Text(
                  'Confidence Threshold: ',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2C3E50),
                  ),
                ),
                Text(
                  '${_confidenceThreshold.round()}%',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF8B5CF6),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Slider(
              value: _confidenceThreshold,
              min: 0,
              max: 100,
              divisions: 100,
              activeColor: const Color(0xFF8B5CF6),
              inactiveColor: Colors.grey.shade300,
              onChanged:
                  (value) => setState(() => _confidenceThreshold = value),
            ),

            const SizedBox(height: 32),

            // Analyze Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isAnalyzing ? null : _analyzeEmotion,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF8B5CF6),
                  foregroundColor: Colors.white,
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child:
                    _isAnalyzing
                        ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                        : Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.info_outline),
                            const SizedBox(width: 8),
                            const Text(
                              'Analyze Emotion',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecordVoiceTab() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.mic, color: Color(0xFF8B5CF6), size: 64),
            const SizedBox(height: 24),
            const Text(
              'Record Voice',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2C3E50),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Tap the microphone to start recording your baby\'s voice for emotion analysis.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Color(0xFF7F8C8D)),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Voice recording functionality coming soon!',
                      ),
                      backgroundColor: Color(0xFF8B5CF6),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF8B5CF6),
                  foregroundColor: Colors.white,
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  'Start Recording',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryTab() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.history, color: Color(0xFF8B5CF6), size: 64),
            const SizedBox(height: 24),
            const Text(
              'Analysis History',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2C3E50),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'View your previous emotion analysis results and track your baby\'s emotional development over time.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Color(0xFF7F8C8D)),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('History functionality coming soon!'),
                      backgroundColor: Color(0xFF8B5CF6),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF8B5CF6),
                  foregroundColor: Colors.white,
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  'View History',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _selectFile() {
    // Simulate file selection
    setState(() {
      _selectedFileName = 'Recording.wav';
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('File selected: Recording.wav'),
        backgroundColor: Color(0xFF8B5CF6),
      ),
    );
  }

  void _analyzeEmotion() async {
    if (_selectedFileName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select an audio file first'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isAnalyzing = true;
    });

    // Simulate analysis
    await Future.delayed(const Duration(seconds: 3));

    setState(() {
      _isAnalyzing = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Emotion analysis completed! Confidence: ${_confidenceThreshold.round()}%',
        ),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _showProfileDialog() {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text(
              'Profile Information',
              style: TextStyle(
                color: Color(0xFF8B5CF6),
                fontWeight: FontWeight.bold,
              ),
            ),
            content: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  _buildProfileItem(
                    'Parent Name',
                    widget.userData['parentName'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Parent Phone',
                    widget.userData['parentPhone'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Parent Email',
                    widget.userData['parentEmail'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Child Name',
                    widget.userData['childName'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Child Phone',
                    widget.userData['childPhone'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Child Age',
                    widget.userData['childAge'] ?? 'N/A',
                  ),
                  _buildProfileItem(
                    'Relationship',
                    widget.userData['relationship'] ?? 'N/A',
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text(
                  'Close',
                  style: TextStyle(color: Color(0xFF8B5CF6)),
                ),
              ),
            ],
          ),
    );
  }

  Widget _buildProfileItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Color(0xFF2C3E50),
            ),
          ),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(color: Color(0xFF7F8C8D))),
        ],
      ),
    );
  }
}
