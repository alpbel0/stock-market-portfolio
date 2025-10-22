import 'package:shared_preferences/shared_preferences.dart';
import '../core/api_client.dart';
import '../models/user.dart';

class AuthService {
  final ApiClient _apiClient;
  final SharedPreferences _prefs;

  AuthService(this._apiClient, this._prefs);

  /// Login with email and password
  Future<User> login(String email, String password) async {
    try {
      final response = await _apiClient.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      final accessToken = response.data['access_token'] as String;
      final refreshToken = response.data['refresh_token'] as String;
      final userData = response.data['user'] as Map<String, dynamic>;

      // Save tokens
      await _prefs.setString('access_token', accessToken);
      await _prefs.setString('refresh_token', refreshToken);

      return User.fromJson(userData);
    } catch (e) {
      throw Exception('Giriş başarısız: $e');
    }
  }

  /// Register new user
  Future<User> register({
    required String email,
    required String password,
    String? name,
  }) async {
    try {
      final response = await _apiClient.post(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          if (name != null) 'name': name,
        },
      );

      final accessToken = response.data['access_token'] as String;
      final refreshToken = response.data['refresh_token'] as String;
      final userData = response.data['user'] as Map<String, dynamic>;

      // Save tokens
      await _prefs.setString('access_token', accessToken);
      await _prefs.setString('refresh_token', refreshToken);

      return User.fromJson(userData);
    } catch (e) {
      throw Exception('Kayıt başarısız: $e');
    }
  }

  /// Logout user
  Future<void> logout() async {
    try {
      // Call logout endpoint
      await _apiClient.post('/auth/logout');
    } catch (e) {
      // Continue with local logout even if API fails
    } finally {
      // Clear local storage
      await _prefs.remove('access_token');
      await _prefs.remove('refresh_token');
      await _prefs.remove('user_id');
      await _prefs.remove('user_email');
    }
  }

  /// Refresh access token
  Future<String?> refreshToken() async {
    try {
      final refreshToken = _prefs.getString('refresh_token');
      if (refreshToken == null) return null;

      final response = await _apiClient.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newAccessToken = response.data['access_token'] as String;
      final newRefreshToken = response.data['refresh_token'] as String;

      // Save new tokens
      await _prefs.setString('access_token', newAccessToken);
      await _prefs.setString('refresh_token', newRefreshToken);

      return newAccessToken;
    } catch (e) {
      // If refresh fails, user needs to login again
      await logout();
      return null;
    }
  }

  /// Check if user is logged in
  bool isLoggedIn() {
    final token = _prefs.getString('access_token');
    return token != null && token.isNotEmpty;
  }

  /// Get current user info
  Future<User?> getCurrentUser() async {
    if (!isLoggedIn()) return null;

    try {
      final response = await _apiClient.get('/auth/me');
      return User.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      return null;
    }
  }
}