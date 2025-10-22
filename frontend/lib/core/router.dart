import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/auth/onboarding_screen.dart';
import '../screens/home/home_screen.dart';

class AppRouter {
  static GoRouter createRouter({required bool isAuthenticated}) {
    return GoRouter(
      initialLocation: isAuthenticated ? '/home' : '/onboarding',
      redirect: (context, state) {
        final isAuthRoute = state.matchedLocation.startsWith('/auth') ||
            state.matchedLocation == '/onboarding' ||
            state.matchedLocation == '/login' ||
            state.matchedLocation == '/register';

        // If user is authenticated and trying to access auth routes, redirect to home
        if (isAuthenticated && isAuthRoute) {
          return '/home';
        }

        // If user is not authenticated and trying to access protected routes, redirect to login
        if (!isAuthenticated && !isAuthRoute) {
          return '/login';
        }

        return null; // No redirect needed
      },
      routes: [
        // Onboarding
        GoRoute(
          path: '/onboarding',
          name: 'onboarding',
          builder: (context, state) => const OnboardingScreen(),
        ),

        // Auth Routes
        GoRoute(
          path: '/login',
          name: 'login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/register',
          name: 'register',
          builder: (context, state) => const RegisterScreen(),
        ),

        // Home (Protected)
        GoRoute(
          path: '/home',
          name: 'home',
          builder: (context, state) => const HomeScreen(),
        ),

        // Portfolio (Protected)
        GoRoute(
          path: '/portfolio',
          name: 'portfolio',
          builder: (context, state) => const Scaffold(
            body: Center(child: Text('Portfolio Screen')),
          ),
        ),

        // Market (Protected)
        GoRoute(
          path: '/market',
          name: 'market',
          builder: (context, state) => const Scaffold(
            body: Center(child: Text('Market Screen')),
          ),
        ),

        // Profile (Protected)
        GoRoute(
          path: '/profile',
          name: 'profile',
          builder: (context, state) => const Scaffold(
            body: Center(child: Text('Profile Screen')),
          ),
        ),
      ],
      errorBuilder: (context, state) => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                '404 - Sayfa Bulunamadı',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.go('/home'),
                child: const Text('Ana Sayfaya Dön'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}