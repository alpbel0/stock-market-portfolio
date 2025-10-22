import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/portfolio.dart';
import '../services/portfolio_service.dart';

/// Portfolio State
class PortfolioState {
  final List<Portfolio> portfolios;
  final Portfolio? selectedPortfolio;
  final bool isLoading;
  final String? error;
  
  // Sentinel nesnesi: copyWith'ta 'parametre verilmedi' ile 'bilerek null verildi' ayrımını yapmak için
  static const _sentinel = Object();

  PortfolioState({
    this.portfolios = const [],
    this.selectedPortfolio,
    this.isLoading = false,
    this.error,
  });

  PortfolioState copyWith({
    List<Portfolio>? portfolios,
    Object? selectedPortfolio = _sentinel,
    bool? isLoading,
    Object? error = _sentinel,
  }) {
    return PortfolioState(
      portfolios: portfolios ?? this.portfolios,
      selectedPortfolio: identical(selectedPortfolio, _sentinel)
          ? this.selectedPortfolio
          : selectedPortfolio as Portfolio?,
      isLoading: isLoading ?? this.isLoading,
      error: identical(error, _sentinel) ? this.error : error as String?,
    );
  }

  bool get hasPortfolios => portfolios.isNotEmpty;
  
  double get totalValue {
    return portfolios.fold(
      0.0,
      (sum, portfolio) => sum + portfolio.totalValue,
    );
  }
  
  double get totalProfitLoss {
    return portfolios.fold(
      0.0,
      (sum, portfolio) => sum + portfolio.profitLoss,
    );
  }
}

/// Portfolio Provider
class PortfolioNotifier extends StateNotifier<PortfolioState> {
  final PortfolioService _portfolioService;

  PortfolioNotifier(this._portfolioService) : super(PortfolioState());

  /// Load all portfolios
  Future<void> loadPortfolios() async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final portfolios = await _portfolioService.getPortfolios();
      
      state = state.copyWith(
        portfolios: portfolios,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Create new portfolio
  Future<void> createPortfolio({
    required String name,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final newPortfolio = await _portfolioService.createPortfolio(
        name: name,
        description: description,
      );
      
      state = state.copyWith(
        portfolios: [...state.portfolios, newPortfolio],
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

  /// Update portfolio
  Future<void> updatePortfolio({
    required String portfolioId,
    String? name,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final updatedPortfolio = await _portfolioService.updatePortfolio(
        portfolioId: portfolioId,
        name: name,
        description: description,
      );
      
      final updatedList = state.portfolios.map((portfolio) {
        return portfolio.id == portfolioId ? updatedPortfolio : portfolio;
      }).toList();
      
      state = state.copyWith(
        portfolios: updatedList,
        selectedPortfolio: state.selectedPortfolio?.id == portfolioId
            ? updatedPortfolio
            : state.selectedPortfolio,
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

  /// Delete portfolio
  Future<void> deletePortfolio(String portfolioId) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      await _portfolioService.deletePortfolio(portfolioId);
      
      final updatedList = state.portfolios
          .where((portfolio) => portfolio.id != portfolioId)
          .toList();
      
      state = state.copyWith(
        portfolios: updatedList,
        selectedPortfolio: state.selectedPortfolio?.id == portfolioId
            ? null
            : state.selectedPortfolio,
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

  /// Select portfolio
  void selectPortfolio(Portfolio portfolio) {
    state = state.copyWith(selectedPortfolio: portfolio);
  }

  /// Clear selected portfolio
  void clearSelection() {
    state = state.copyWith(selectedPortfolio: null);
  }

  /// Refresh portfolios
  Future<void> refresh() async {
    await loadPortfolios();
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }
}
