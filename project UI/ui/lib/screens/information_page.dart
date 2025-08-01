import 'package:flutter/material.dart';
import 'signin_page.dart';
import 'signup_page.dart';

class InformationPage extends StatelessWidget {
  const InformationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFE8F4FD), Color(0xFFFFF5F5)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                const SizedBox(height: 40),
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(60),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.blue.withOpacity(0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.child_care,
                          size: 60,
                          color: Color(0xFF4A90E2),
                        ),
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'Baby Emotions',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2C3E50),
                        ),
                      ),
                      const Text(
                        'Understanding Your Little One\'s Feelings',
                        style: TextStyle(
                          fontSize: 16,
                          color: Color(0xFF7F8C8D),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 40),

                // Information Cards
                _buildInfoCard(
                  icon: Icons.favorite,
                  title: 'Emotional Development',
                  description:
                      'Babies experience a wide range of emotions from birth. Understanding these emotions helps parents provide better care and support.',
                  color: const Color(0xFFE74C3C),
                ),

                const SizedBox(height: 20),

                _buildInfoCard(
                  icon: Icons.psychology,
                  title: 'Reading Baby Cues',
                  description:
                      'Learn to recognize different cries, facial expressions, and body language to understand what your baby is trying to communicate.',
                  color: const Color(0xFF3498DB),
                ),

                const SizedBox(height: 20),

                _buildInfoCard(
                  icon: Icons.family_restroom,
                  title: 'Parent-Child Bonding',
                  description:
                      'Strong emotional bonds between parents and babies are crucial for healthy development and emotional well-being.',
                  color: const Color(0xFF2ECC71),
                ),

                const SizedBox(height: 20),

                _buildInfoCard(
                  icon: Icons.timeline,
                  title: 'Milestone Tracking',
                  description:
                      'Track your baby\'s emotional milestones and development stages to ensure they\'re progressing healthily.',
                  color: const Color(0xFFF39C12),
                ),

                const SizedBox(height: 40),

                // Action Buttons
                _buildActionButton(
                  context: context,
                  text: 'Login',
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const SignInPage(),
                      ),
                    );
                  },
                  isPrimary: true,
                ),

                const SizedBox(height: 16),

                _buildActionButton(
                  context: context,
                  text: 'Sign Up',
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const SignUpPage(),
                      ),
                    );
                  },
                  isPrimary: false,
                ),

                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoCard({
    required IconData icon,
    required String title,
    required String description,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 30),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2C3E50),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF7F8C8D),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required BuildContext context,
    required String text,
    required VoidCallback onPressed,
    required bool isPrimary,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isPrimary ? const Color(0xFF4A90E2) : Colors.white,
          foregroundColor: isPrimary ? Colors.white : const Color(0xFF4A90E2),
          elevation: isPrimary ? 4 : 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side:
                isPrimary
                    ? BorderSide.none
                    : const BorderSide(color: Color(0xFF4A90E2), width: 2),
          ),
        ),
        child: Text(
          text,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
