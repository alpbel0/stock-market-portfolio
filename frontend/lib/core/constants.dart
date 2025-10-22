import 'package:flutter/material.dart';

// API Configuration
class ApiConstants {
  static const String baseUrl = 'http://localhost:8000/api';
  static const String apiVersion = 'v1';
  
  // Endpoints
  static const String authEndpoint = '/auth';
  static const String portfolioEndpoint = '/portfolio';
  static const String marketEndpoint = '/market';
  static const String transactionEndpoint = '/transactions';
  
  // Timeout
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}

// App Colors
class AppColors {
  // Primary Colors
  static const Color primary = Color(0xFF6366F1);
  static const Color primaryDark = Color(0xFF4F46E5);
  static const Color primaryLight = Color(0xFF818CF8);
  
  // Background Colors
  static const Color background = Color(0xFFF9FAFB);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF1F2937);
  
  // Text Colors
  static const Color textPrimary = Color(0xFF111827);
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color textDisabled = Color(0xFF9CA3AF);
  
  // Status Colors
  static const Color success = Color(0xFF10B981);
  static const Color error = Color(0xFFEF4444);
  static const Color warning = Color(0xFFF59E0B);
  static const Color info = Color(0xFF3B82F6);
  
  // Chart Colors
  static const List<Color> chartColors = [
    Color(0xFF6366F1),
    Color(0xFF8B5CF6),
    Color(0xFFEC4899),
    Color(0xFFF59E0B),
    Color(0xFF10B981),
  ];
}

// App Strings
class AppStrings {
  // App
  static const String appName = 'Portfolio App';
  static const String appVersion = '1.0.0';
  
  // Auth
  static const String login = 'Giriş Yap';
  static const String register = 'Kayıt Ol';
  static const String logout = 'Çıkış Yap';
  static const String email = 'E-posta';
  static const String password = 'Şifre';
  static const String forgotPassword = 'Şifremi Unuttum';
  
  // Portfolio
  static const String portfolio = 'Portföy';
  static const String myPortfolio = 'Portföyüm';
  static const String totalValue = 'Toplam Değer';
  static const String dailyChange = 'Günlük Değişim';
  static const String assets = 'Varlıklar';
  
  // Market
  static const String market = 'Piyasa';
  static const String stocks = 'Hisse Senetleri';
  static const String crypto = 'Kripto Paralar';
  static const String forex = 'Döviz';
  
  // Transactions
  static const String transactions = 'İşlemler';
  static const String buy = 'Al';
  static const String sell = 'Sat';
  static const String amount = 'Miktar';
  static const String price = 'Fiyat';
  
  // Common
  static const String loading = 'Yükleniyor...';
  static const String error = 'Hata';
  static const String retry = 'Tekrar Dene';
  static const String cancel = 'İptal';
  static const String save = 'Kaydet';
  static const String delete = 'Sil';
  static const String edit = 'Düzenle';
  static const String search = 'Ara';
  static const String filter = 'Filtrele';
  static const String sort = 'Sırala';
}

// Storage Keys
class StorageKeys {
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String userId = 'user_id';
  static const String userEmail = 'user_email';
  static const String isDarkMode = 'is_dark_mode';
  static const String language = 'language';
}