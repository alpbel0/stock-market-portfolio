class Portfolio {
  final String id;
  final String name;
  final String? description;
  final String userId;
  final double totalValue;
  final double totalCost;
  final double profitLoss;
  final double profitLossPercentage;
  final DateTime createdAt;
  final DateTime updatedAt;

  Portfolio({
    required this.id,
    required this.name,
    this.description,
    required this.userId,
    required this.totalValue,
    required this.totalCost,
    required this.profitLoss,
    required this.profitLossPercentage,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Portfolio.fromJson(Map<String, dynamic> json) {
    return Portfolio(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      userId: json['user_id'] as String,
      totalValue: (json['total_value'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      profitLoss: (json['profit_loss'] as num).toDouble(),
      profitLossPercentage: (json['profit_loss_percentage'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'user_id': userId,
      'total_value': totalValue,
      'total_cost': totalCost,
      'profit_loss': profitLoss,
      'profit_loss_percentage': profitLossPercentage,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Portfolio copyWith({
    String? id,
    String? name,
    String? description,
    String? userId,
    double? totalValue,
    double? totalCost,
    double? profitLoss,
    double? profitLossPercentage,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Portfolio(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      userId: userId ?? this.userId,
      totalValue: totalValue ?? this.totalValue,
      totalCost: totalCost ?? this.totalCost,
      profitLoss: profitLoss ?? this.profitLoss,
      profitLossPercentage: profitLossPercentage ?? this.profitLossPercentage,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  bool get isProfitable => profitLoss > 0;
  bool get isLoss => profitLoss < 0;
}

class PortfolioSummary {
  final String portfolioId;
  final String portfolioName;
  final double totalValue;
  final double totalCost;
  final double profitLoss;
  final double profitLossPercentage;
  final double dailyChange;
  final double dailyChangePercentage;
  final int assetCount;
  final List<AssetSummary> topAssets;

  PortfolioSummary({
    required this.portfolioId,
    required this.portfolioName,
    required this.totalValue,
    required this.totalCost,
    required this.profitLoss,
    required this.profitLossPercentage,
    required this.dailyChange,
    required this.dailyChangePercentage,
    required this.assetCount,
    required this.topAssets,
  });

  factory PortfolioSummary.fromJson(Map<String, dynamic> json) {
    return PortfolioSummary(
      portfolioId: json['portfolio_id'] as String,
      portfolioName: json['portfolio_name'] as String,
      totalValue: (json['total_value'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      profitLoss: (json['profit_loss'] as num).toDouble(),
      profitLossPercentage: (json['profit_loss_percentage'] as num).toDouble(),
      dailyChange: (json['daily_change'] as num).toDouble(),
      dailyChangePercentage: (json['daily_change_percentage'] as num).toDouble(),
      assetCount: json['asset_count'] as int,
      topAssets: (json['top_assets'] as List<dynamic>)
          .map((item) => AssetSummary.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class AssetSummary {
  final String symbol;
  final String name;
  final double currentPrice;
  final double quantity;
  final double totalValue;
  final double profitLoss;
  final double profitLossPercentage;

  AssetSummary({
    required this.symbol,
    required this.name,
    required this.currentPrice,
    required this.quantity,
    required this.totalValue,
    required this.profitLoss,
    required this.profitLossPercentage,
  });

  factory AssetSummary.fromJson(Map<String, dynamic> json) {
    return AssetSummary(
      symbol: json['symbol'] as String,
      name: json['name'] as String,
      currentPrice: (json['current_price'] as num).toDouble(),
      quantity: (json['quantity'] as num).toDouble(),
      totalValue: (json['total_value'] as num).toDouble(),
      profitLoss: (json['profit_loss'] as num).toDouble(),
      profitLossPercentage: (json['profit_loss_percentage'] as num).toDouble(),
    );
  }
}