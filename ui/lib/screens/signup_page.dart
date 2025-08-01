import 'package:flutter/material.dart';

class SignUpPage extends StatefulWidget {
  const SignUpPage({super.key});

  @override
  State<SignUpPage> createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  String? selectedUserType;
  final _formKey = GlobalKey<FormState>();
  final _parentNameController = TextEditingController();
  final _parentNumberController = TextEditingController();
  final _parentEmailController = TextEditingController();
  final _parentPasswordController = TextEditingController();
  final _childNumberController = TextEditingController();
  final _childAgeController = TextEditingController();
  final _childNameController = TextEditingController();
  final _childParentNameController = TextEditingController();
  final _childParentNumberController = TextEditingController();
  final _childParentPasswordController = TextEditingController();
  String? selectedRelation;
  bool _isLoading = false;
  bool _obscureParentPassword = true;
  bool _obscureChildParentPassword = true;

  final List<String> relationshipOptions = [
    'Mother',
    'Father',
    'Grandmother (Maternal)',
    'Grandfather (Maternal)',
    'Grandmother (Paternal)',
    'Grandfather (Paternal)',
    'Aunt (Maternal)',
    'Uncle (Maternal)',
    'Aunt (Paternal)',
    'Uncle (Paternal)',
    'Sister',
    'Brother',
    'Step Mother',
    'Step Father',
    'Foster Parent',
    'Legal Guardian',
    'Caregiver',
    'Nanny',
    'Other Family Member',
  ];

  @override
  void dispose() {
    _parentNameController.dispose();
    _parentNumberController.dispose();
    _parentEmailController.dispose();
    _parentPasswordController.dispose();
    _childNumberController.dispose();
    _childAgeController.dispose();
    _childNameController.dispose();
    _childParentNameController.dispose();
    _childParentNumberController.dispose();
    _childParentPasswordController.dispose();
    super.dispose();
  }

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
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Back Button and Header
                  Row(
                    children: [
                      IconButton(
                        onPressed: () => Navigator.pop(context),
                        icon: const Icon(
                          Icons.arrow_back_ios,
                          color: Color(0xFF4A90E2),
                        ),
                      ),
                      const Expanded(
                        child: Text(
                          'Sign Up',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2C3E50),
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      const SizedBox(width: 48), // Balance the back button
                    ],
                  ),

                  const SizedBox(height: 40),

                  // User Type Selection
                  const Text(
                    'I am a:',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2C3E50),
                    ),
                  ),
                  const SizedBox(height: 16),

                  Row(
                    children: [
                      Expanded(
                        child: _buildUserTypeCard(
                          title: 'Parent',
                          icon: Icons.family_restroom,
                          isSelected: selectedUserType == 'parent',
                          onTap:
                              () => setState(() => selectedUserType = 'parent'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildUserTypeCard(
                          title: 'Baby',
                          icon: Icons.child_care,
                          isSelected: selectedUserType == 'baby',
                          onTap:
                              () => setState(() => selectedUserType = 'baby'),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 40),

                  // Parent Form Fields
                  if (selectedUserType == 'parent') ...[
                    _buildTextField(
                      controller: _parentNameController,
                      label: 'Parent Name',
                      hint: 'Enter your full name',
                      icon: Icons.person,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your name';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _parentEmailController,
                      label: 'Parent Email',
                      hint: 'Enter your email address',
                      icon: Icons.email,
                      keyboardType: TextInputType.emailAddress,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        if (!RegExp(
                          r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$',
                        ).hasMatch(value)) {
                          return 'Please enter a valid email';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _parentNumberController,
                      label: 'Parent Phone Number',
                      hint: 'Enter your phone number',
                      icon: Icons.phone,
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your phone number';
                        }
                        if (value.length < 10) {
                          return 'Please enter a valid phone number';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildPasswordField(
                      controller: _parentPasswordController,
                      label: 'Password',
                      hint: 'Enter your password',
                      obscureText: _obscureParentPassword,
                      onToggle:
                          () => setState(
                            () =>
                                _obscureParentPassword =
                                    !_obscureParentPassword,
                          ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _childNameController,
                      label: 'Child Name',
                      hint: 'Enter child\'s full name',
                      icon: Icons.child_care,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter child\'s name';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _childNumberController,
                      label: 'Child Phone Number',
                      hint: 'Enter child\'s phone number',
                      icon: Icons.phone_android,
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter child\'s phone number';
                        }
                        if (value.length < 10) {
                          return 'Please enter a valid phone number';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _childAgeController,
                      label: 'Child Age',
                      hint: 'Enter child\'s age in months',
                      icon: Icons.cake,
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter child\'s age';
                        }
                        final age = int.tryParse(value);
                        if (age == null || age < 0 || age > 72) {
                          return 'Please enter a valid age (0-72 months)';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    // Relationship Dropdown
                    const Text(
                      'Relationship with Child',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2C3E50),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: selectedRelation,
                          hint: const Text(
                            'Select your relationship',
                            style: TextStyle(color: Color(0xFF7F8C8D)),
                          ),
                          isExpanded: true,
                          icon: const Icon(Icons.keyboard_arrow_down),
                          items:
                              relationshipOptions.map((String relation) {
                                return DropdownMenuItem<String>(
                                  value: relation,
                                  child: Text(relation),
                                );
                              }).toList(),
                          onChanged: (String? newValue) {
                            setState(() {
                              selectedRelation = newValue;
                            });
                          },
                        ),
                      ),
                    ),

                    const SizedBox(height: 40),

                    // Submit Button
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleParentSubmit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF4A90E2),
                          foregroundColor: Colors.white,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child:
                            _isLoading
                                ? const SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                                : const Text(
                                  'Sign Up',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                      ),
                    ),
                  ],

                  // Child Form Fields
                  if (selectedUserType == 'baby') ...[
                    _buildTextField(
                      controller: _childParentNameController,
                      label: 'Parent Name',
                      hint: 'Enter your parent\'s full name',
                      icon: Icons.person,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter parent\'s name';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildTextField(
                      controller: _childParentNumberController,
                      label: 'Parent Phone Number',
                      hint: 'Enter your parent\'s phone number',
                      icon: Icons.phone,
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter parent\'s phone number';
                        }
                        if (value.length < 10) {
                          return 'Please enter a valid phone number';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    _buildPasswordField(
                      controller: _childParentPasswordController,
                      label: 'Parent Password',
                      hint: 'Enter your parent\'s password',
                      obscureText: _obscureChildParentPassword,
                      onToggle:
                          () => setState(
                            () =>
                                _obscureChildParentPassword =
                                    !_obscureChildParentPassword,
                          ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter parent\'s password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 40),

                    // Submit Button for Child
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleChildSubmit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF4A90E2),
                          foregroundColor: Colors.white,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child:
                            _isLoading
                                ? const SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                                : const Text(
                                  'Sign Up',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                      ),
                    ),
                  ],

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildUserTypeCard({
    required String title,
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF4A90E2) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? const Color(0xFF4A90E2) : Colors.grey.shade300,
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(
              icon,
              size: 40,
              color: isSelected ? Colors.white : const Color(0xFF4A90E2),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: isSelected ? Colors.white : const Color(0xFF2C3E50),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Color(0xFF2C3E50),
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon, color: const Color(0xFF4A90E2)),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade300),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade300),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF4A90E2), width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.red, width: 2),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPasswordField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required bool obscureText,
    required VoidCallback onToggle,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Color(0xFF2C3E50),
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: const Icon(Icons.lock, color: Color(0xFF4A90E2)),
            suffixIcon: IconButton(
              icon: Icon(
                obscureText ? Icons.visibility : Icons.visibility_off,
                color: const Color(0xFF4A90E2),
              ),
              onPressed: onToggle,
            ),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade300),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey.shade300),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF4A90E2), width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.red, width: 2),
            ),
          ),
        ),
      ],
    );
  }

  void _handleParentSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (selectedRelation == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select your relationship with the child'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
    });

    // Show success message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Parent sign up successful! Welcome to Baby Emotions!'),
        backgroundColor: Colors.green,
      ),
    );

    // TODO: Navigate to main app or dashboard
    // Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => DashboardPage()));
  }

  void _handleChildSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
    });

    // Show success message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Child sign up successful! Welcome to Baby Emotions!'),
        backgroundColor: Colors.green,
      ),
    );

    // TODO: Navigate to main app or dashboard
    // Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => DashboardPage()));
  }
}
