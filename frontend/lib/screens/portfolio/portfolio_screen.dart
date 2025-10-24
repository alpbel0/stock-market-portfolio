import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'portfolio_detail_screen.dart';
import 'add_portfolio_screen.dart';

class PortfolioScreen extends ConsumerStatefulWidget {
  const PortfolioScreen({super.key});

  @override
  ConsumerState<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends ConsumerState<PortfolioScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  bool _isRefreshing = false;

  // Mock portfolio data
  final List<Map<String, dynamic>> _portfolios = [
    {
      'id': '1',
      'name': 'Uzun Vadeli Yatırımlar',
      'description': 'Emeklilik için uzun vadeli portföy',
      'totalValue': 125430.50,
      'dailyChange': 2450.30,
      'dailyChangePercent': 2.0,
      'assetCount': 12,
    },
    {
      'id': '2',
      'name': 'Kısa Vadeli',
      'description': 'Aktif alım satım portföyü',
      'totalValue': 45230.75,
      'dailyChange': -850.20,
      'dailyChangePercent': -1.8,
      'assetCount': 8,
    },
    {
      'id': '3',
      'name': 'Kripto Portföy',
      'description': 'Kripto para yatırımları',
      'totalValue': 23450.00,
      'dailyChange': 1250.80,
      'dailyChangePercent': 5.6,
      'assetCount': 5,
    },
  ];

  List<Map<String, dynamic>> get _filteredPortfolios {
    if (_searchQuery.isEmpty) {
      return _portfolios;
    }
    return _portfolios.where((portfolio) {
      final name = portfolio['name'].toString().toLowerCase();
      final description = portfolio['description'].toString().toLowerCase();
      final query = _searchQuery.toLowerCase();
      return name.contains(query) || description.contains(query);
    }).toList();
  }

  Future<void> _handleRefresh() async {
    setState(() => _isRefreshing = true);
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    setState(() => _isRefreshing = false);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Portföyler güncellendi')),
      );
    }
  }

  void _navigateToAddPortfolio() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AddPortfolioScreen(),
      ),
    );
  }

  void _navigateToPortfolioDetail(Map<String, dynamic> portfolio) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PortfolioDetailScreen(portfolio: portfolio),
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isTablet = MediaQuery.of(context).size.width >= 600;

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _handleRefresh,
        child: CustomScrollView(
          slivers: [
            // Search Bar
            SliverToBoxAdapter(
              child: Padding(
                padding: EdgeInsets.all(isTablet ? 24.0 : 16.0),
                child: TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Portföy ara...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              setState(() {
                                _searchController.clear();
                                _searchQuery = '';
                              });
                            },
                          )
                        : null,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onChanged: (value) {
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
              ),
            ),

            // Portfolio Cards
            _filteredPortfolios.isEmpty
                ? SliverFillRemaining(
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.search_off,
                            size: 64,
                            color: theme.colorScheme.outline,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Portföy bulunamadı',
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: theme.colorScheme.outline,
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                : SliverPadding(
                    padding: EdgeInsets.symmetric(
                      horizontal: isTablet ? 24.0 : 16.0,
                      vertical: 8.0,
                    ),
                    sliver: SliverList(
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final portfolio = _filteredPortfolios[index];
                          return _PortfolioCard(
                            portfolio: portfolio,
                            onTap: () => _navigateToPortfolioDetail(portfolio),
                          );
                        },
                        childCount: _filteredPortfolios.length,
                      ),
                    ),
                  ),

            // Bottom padding
            const SliverToBoxAdapter(
              child: SizedBox(height: 80),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToAddPortfolio,
        icon: const Icon(Icons.add),
        label: const Text('Yeni Portföy'),
      ),
    );
  }
}

class _PortfolioCard extends StatelessWidget {
  final Map<String, dynamic> portfolio;
  final VoidCallback onTap;

  const _PortfolioCard({
    required this.portfolio,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPositive = portfolio['dailyChange'] >= 0;
    final changeColor = isPositive ? Colors.green[600] : Colors.red[600];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          portfolio['name'],
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          portfolio['description'],
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.outline,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: theme.colorScheme.outline,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Toplam Değer',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '₺${portfolio['totalValue'].toStringAsFixed(2)}',
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Row(
                        children: [
                          Icon(
                            isPositive ? Icons.trending_up : Icons.trending_down,
                            color: changeColor,
                            size: 20,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${isPositive ? '+' : ''}${portfolio['dailyChange'].toStringAsFixed(2)}',
                            style: TextStyle(
                              color: changeColor,
                              fontWeight: FontWeight.w600,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${isPositive ? '+' : ''}${portfolio['dailyChangePercent'].toStringAsFixed(1)}%',
                        style: TextStyle(
                          color: changeColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.account_balance_wallet_outlined,
                    size: 16,
                    color: theme.colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${portfolio['assetCount']} varlık',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}