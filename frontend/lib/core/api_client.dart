import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'constants.dart';

class ApiClient {
  late final Dio _dio;
  final SharedPreferences _prefs;
  
  ApiClient(this._prefs) {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: ApiConstants.connectionTimeout,
        receiveTimeout: ApiConstants.receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );
    
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add access token to headers
          final token = _prefs.getString(StorageKeys.accessToken);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          
          return handler.next(options);
        },
        onError: (error, handler) async {
          // Handle 401 Unauthorized - Token expired
          if (error.response?.statusCode == 401) {
            // Try to refresh token
            final refreshed = await _refreshToken();
            
            if (refreshed) {
              // Retry the original request
              final options = error.requestOptions;
              final token = _prefs.getString(StorageKeys.accessToken);
              options.headers['Authorization'] = 'Bearer $token';
              
              try {
                final response = await _dio.fetch(options);
                return handler.resolve(response);
              } catch (e) {
                return handler.reject(error);
              }
            }
          }
          
          return handler.next(error);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
      ),
    );
    
    // Add logging interceptor in debug mode
    _dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: false,
        error: true,
        logPrint: (obj) => print('[API] $obj'),
      ),
    );
  }
  
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = _prefs.getString(StorageKeys.refreshToken);
      if (refreshToken == null) return false;
      
      final response = await _dio.post(
        '${ApiConstants.authEndpoint}/refresh',
        data: {'refresh_token': refreshToken},
      );
      
      if (response.statusCode == 200) {
        final newAccessToken = response.data['access_token'];
        final newRefreshToken = response.data['refresh_token'];
        
        await _prefs.setString(StorageKeys.accessToken, newAccessToken);
        await _prefs.setString(StorageKeys.refreshToken, newRefreshToken);
        
        return true;
      }
      
      return false;
    } catch (e) {
      print('[API] Token refresh failed: $e');
      return false;
    }
  }
  
  // GET Request
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // POST Request
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // PUT Request
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // DELETE Request
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // PATCH Request
  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.patch<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  // Error Handler
  ApiException _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'Bağlantı zaman aşımına uğradı',
          statusCode: error.response?.statusCode,
        );
      
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final message = error.response?.data?['message'] ?? 'Bir hata oluştu';
        
        return ApiException(
          message: message,
          statusCode: statusCode,
        );
      
      case DioExceptionType.cancel:
        return ApiException(
          message: 'İstek iptal edildi',
          statusCode: error.response?.statusCode,
        );
      
      case DioExceptionType.connectionError:
        return ApiException(
          message: 'Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin',
          statusCode: error.response?.statusCode,
        );
      
      case DioExceptionType.badCertificate:
        return ApiException(
          message: 'Güvenlik sertifikası hatası',
          statusCode: error.response?.statusCode,
        );
      
      case DioExceptionType.unknown:
      default:
        return ApiException(
          message: error.message ?? 'Bilinmeyen bir hata oluştu',
          statusCode: error.response?.statusCode,
        );
    }
  }
}

// Custom API Exception
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  
  ApiException({
    required this.message,
    this.statusCode,
  });
  
  @override
  String toString() => message;
}