# Baby Emotions App

A Flutter application designed to help parents understand and track their baby's emotional development.

## Features

- **Information Page**: Comprehensive information about baby emotions and development
- **Sign In Page**: User authentication with parent/baby selection and detailed form
- **Sign Up Page**: New user registration with comprehensive family information
- **Beautiful UI**: Modern, child-friendly design with gradient backgrounds
- **Responsive Design**: Works on various screen sizes
- **Form Validation**: Comprehensive input validation for all fields

## Project Structure

```
lib/
├── main.dart                 # Main application entry point
└── screens/
    ├── information_page.dart # Information page with login/signup buttons
    ├── signin_page.dart      # Sign in page with parent/baby selection
    └── signup_page.dart      # Sign up page for new user registration
```

## Getting Started

### Prerequisites

- Flutter SDK (version 3.7.2 or higher)
- Dart SDK
- Android Studio / VS Code
- Android Emulator or physical device

### Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd ui
   ```

3. Install dependencies:
   ```bash
   flutter pub get
   ```

4. Run the application:
   ```bash
   flutter run
   ```

## App Features

### Information Page
The main page provides valuable information about:
- **Emotional Development**: Understanding baby emotions from birth
- **Reading Baby Cues**: Recognizing cries, facial expressions, and body language
- **Parent-Child Bonding**: Importance of emotional bonds
- **Milestone Tracking**: Monitoring emotional development stages

### Sign In Page
- **User Type Selection**: Choose between Parent or Baby
- **Parent Form Fields**:
  - Parent Name
  - Parent Phone Number
  - Child Phone Number (Optional)
  - Child Age (in months)
  - Relationship with Child (Dropdown with 19 options)
- **Form Validation**: Comprehensive validation for all fields
- **Loading States**: Visual feedback during form submission

### Sign Up Page
- **User Type Selection**: Choose between Parent or Baby
- **Parent Form Fields**:
  - Parent Name
  - Parent Email
  - Parent Phone Number
  - Child Name
  - Child Phone Number (Optional)
  - Child Age (in months)
  - Relationship with Child (Dropdown with 19 options)
- **Email Validation**: Proper email format validation
- **Form Validation**: Comprehensive validation for all fields

### Relationship Options
The app includes a comprehensive list of relationship options:
- Mother, Father
- Grandmother/Grandfather (Maternal & Paternal)
- Aunt/Uncle (Maternal & Paternal)
- Sister, Brother
- Step Mother, Step Father
- Foster Parent, Legal Guardian
- Caregiver, Nanny
- Other Family Member

### Design Elements
- Soft gradient background (blue to pink)
- Card-based information layout
- Modern button design with hover effects
- Child-friendly color scheme
- Responsive layout
- Form validation with error messages
- Loading indicators
- Smooth navigation transitions

## Future Enhancements

- Baby sign-in/sign-up functionality
- Dashboard for logged-in users
- Baby emotion tracking features
- Development milestone logging
- Parent resources and tips
- Community features
- Data persistence and backend integration

## Technologies Used

- **Flutter**: Cross-platform mobile development framework
- **Dart**: Programming language
- **Material Design**: UI/UX design system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
