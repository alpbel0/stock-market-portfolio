import '../core/api_client.dart';
import '../models/portfolio.dart';

class PortfolioService {
  final ApiClient _apiClient;

  PortfolioService(this._apiClient);

  /// Get all portfolios for current user
  Future<List<Portfolio>> getPortfolios() async {
    try {
      final response = await _apiClient.get('/portfolio');
      
      final portfolios = (response.data as List<dynamic>)
          .map((item) => Portfolio.fromJson(item as Map<String, dynamic>))
          .toList();
      
      return portfolios;
    } catch (e) {
      throw Exception('Portföyler alınamadı: $e');
    }
  }

  /// Create new portfolio
  Future<Portfolio> createPortfolio({
    required String name,
    String? description,
  }) async {
    try {
      final response = await _apiClient.post(
        '/portfolio',
        data: {
          'name': name,
          if (description != null) 'description': description,
        },
      );
      
      return Portfolio.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Portföy oluşturulamadı: $e');
    }
  }

  /// Update existing portfolio
  Future<Portfolio> updatePortfolio({
    required String portfolioId,
    String? name,
    String? description,
  }) async {
    try {
      final response = await _apiClient.put(
        '/portfolio/$portfolioId',
        data: {
          if (name != null) 'name': name,
          if (description != null) 'description': description,
        },
      );
      
      return Portfolio.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Portföy güncellenemedi: $e');
    }
  }

  /// Delete portfolio
  Future<void> deletePortfolio(String portfolioId) async {
    try {
      await _apiClient.delete('/portfolio/$portfolioId');
    } catch (e) {
      throw Exception('Portföy silinemedi: $e');
    }
  }

  /// Get portfolio summary with statistics
  Future<PortfolioSummary> getPortfolioSummary(String portfolioId) async {
    try {
      final response = await _apiClient.get('/portfolio/$portfolioId/summary');
      
      return PortfolioSummary.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Portföy özeti alınamadı: $e');
    }
  }

  /// Get portfolio by ID
  Future<Portfolio> getPortfolioById(String portfolioId) async {
    try {
      final response = await _apiClient.get('/portfolio/$portfolioId');
      
      return Portfolio.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Portföy bulunamadı: $e');
    }
  }
}