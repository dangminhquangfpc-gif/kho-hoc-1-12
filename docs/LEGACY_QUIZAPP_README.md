# QuizApp

A comprehensive quiz application built with Flutter and Firebase, featuring modern UI design and robust functionality.

## Overview

QuizApp is a Quizlet-inspired mobile application that allows users to create, manage, and take quizzes. The app supports multiple study modes including flashcards, practice tests, and timed quizzes with detailed analytics and progress tracking.

## Features

- **Authentication**: Secure user registration and login with Firebase Auth
- **Quiz Management**: Create, edit, and organize quizzes with multiple question types
- **Study Modes**: Flashcards, practice mode, and timed tests
- **Progress Tracking**: Detailed statistics and performance analytics
- **Modern UI**: Material 3 design with light/dark theme support

## Tech Stack

- **Framework**: Flutter/Dart
- **Backend**: Firebase (Authentication, Firestore, Storage)
- **Architecture**: Clean Architecture with MVVM pattern
- **State Management**: Provider
- **UI**: Material 3 with Google Fonts

## Project Structure

```
lib/
├── core/                 # Core utilities and constants
│   ├── constants/
│   ├── themes/
│   └── utils/
├── data/                 # Data layer
│   ├── models/
│   ├── repositories/
│   └── services/
├── domain/               # Business logic layer
│   ├── entities/
│   ├── repositories/
│   └── usecases/
└── presentation/         # UI layer
    ├── screens/
    ├── widgets/
    └── providers/
```

## Firebase Setup

### Prerequisites

1. Flutter SDK installed
2. Firebase CLI installed
3. Firebase project created

### Configuration Steps

1. **Create Firebase Project**
   ```bash
   # Visit Firebase Console and create a new project
   # Project ID: quiz-1155b (or your custom ID)
   ```

2. **Enable Required Services**
   - Authentication (Email/Password)
   - Cloud Firestore (in test mode)
   - Storage (optional, for image uploads)

3. **Configure Android**
   ```bash
   # Download google-services.json from Firebase Console
   # Place it in android/app/google-services.json
   ```

4. **Configure iOS**
   ```bash
   # Download GoogleService-Info.plist from Firebase Console
   # Place it in ios/Runner/GoogleService-Info.plist
   ```

5. **Generate Firebase Options**
   ```bash
   # Install Firebase CLI
   npm install -g firebase-tools
   
   # Login to Firebase
   firebase login
   
   # Configure Flutter project
   dart pub global activate flutterfire_cli
   flutterfire configure
   ```

6. **Install Dependencies**
   ```bash
   flutter pub get
   ```

## Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quizapp
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure Firebase** (follow Firebase Setup section above)

4. **Run the application**
   ```bash
   flutter run
   ```

### Development

- **Run on specific device**
  ```bash
  flutter run -d <device-id>
  ```

- **Build for production**
  ```bash
  # Android
  flutter build apk --release
  
  # iOS
  flutter build ios --release
  
  # Web
  flutter build web
  ```

## Gemini AI Key (setup/rotate)

- File: `lib/data/services/gemini_ai_service.dart`
- Keys to update:
  - `_apiKey`: your Gemini API key from Google AI Studio
  - `_baseUrl`: recommended free-friendly model/endpoint

Example:
```dart
static const String _apiKey = '<YOUR_GEMINI_API_KEY>';
static const String _baseUrl = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent';
```

Notes:
- This API caller is hardcoded directly into a a gemini provider file, it is not safe for production.
- For production, avoid hardcoding keys. Prefer:
  - `flutter_dotenv` (.env), or
  - reading from a local asset (dev only), or
  - routing requests via a backend (Cloud Functions) to keep the key secret.

