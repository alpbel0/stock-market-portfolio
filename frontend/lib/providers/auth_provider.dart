import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

/// Auth State
class AuthState {
  final User? user;
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.isAuthenticated = false,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    bool? isAuthenticated,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Auth Provider
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;

  AuthNotifier(this._authService) : super(AuthState()) {
    _checkAuthStatus();
  }

  /// Check if user is already logged in
  Future<void> _checkAuthStatus() async {
    if (_authService.isLoggedIn()) {
      state = state.copyWith(isLoading: true);
      
      final user = await _authService.getCurrentUser();
      
      if (user != null) {
        state = state.copyWith(
          user: user,
          isAuthenticated: true,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isAuthenticated: false,
          isLoading: false,
        );
      }
    }
  }

  /// Login
  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final user = await _authService.login(email, password);
      
      state = state.copyWith(
        user: user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Register
  Future<void> register({
    required String email,
    required String password,
    String? name,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final user = await _authService.register(
        email: email,
        password: password,
        name: name,
      );
      
      state = state.copyWith(
        user: user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Logout
  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    
    try {
      await _authService.logout();
      
      state = AuthState(); // Reset to initial state
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }
}