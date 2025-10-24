import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PortfolioDetailScreen extends ConsumerStatefulWidget {
  final Map<String, dynamic> portfolio;

  const PortfolioDetailScreen({
    super.key,
    required this.portfolio,
  });

  @override
  ConsumerState<PortfolioDetailScreen> createState() =>
      _PortfolioDetailScreenState();
}

class _PortfolioDetailScreenState extends ConsumerState<PortfolioDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Mock asset data
  final List<Map<String, dynamic>> _assets = [
    {
      'symbol': 'AAPL',
      'name': 'Apple Inc.',
      'quantity': 10,
      'avgPrice': 150.00,
      'currentPrice': 175.50,
      'totalValue': 1755.00,
      'profitLoss': 255.00,
      'profitLossPercent': 17.0,
    },
    {
      'symbol': 'GOOGL',
      'name': 'Alphabet Inc.',
      'quantity': 5,
      'avgPrice': 2500.00,
      'currentPrice': 2650.00,
      'totalValue': 13250.00,
      'profitLoss': 750.00,
      'profitLossPercent': 6.0,
    },
    {
      'symbol': 'MSFT',
      'name': 'Microsoft Corp.',
      'quantity': 8,
      'avgPrice': 300.00,
      'currentPrice': 285.00,
      'totalValue': 2280.00,
      'profitLoss': -120.00,
      'profitLossPercent': -5.0,
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isTablet = MediaQuery.of(context).size.width >= 600;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.portfolio['name']),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () {
              // TODO: Navigate to edit portfolio
            },
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              _showMoreOptions(context);
            },
          ),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // Portfolio Overview
          SliverToBoxAdapter(
            child: _buildPortfolioOverview(theme, isTablet),
          ),

          // Performance Chart
          SliverToBoxAdapter(
            child: _buildPerformanceChart(theme, isTablet),
          ),

          // Tabs (Assets / Transactions)
          SliverToBoxAdapter(
            child: Container(
              margin: EdgeInsets.symmetric(
                horizontal: isTablet ? 24.0 : 16.0,
              ),
              child: TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: 'Varlıklar'),
                  Tab(text: 'İşlemler'),
                ],
              ),
            ),
          ),

          // Asset List
          SliverPadding(
            padding: EdgeInsets.all(isTablet ? 24.0 : 16.0),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final asset = _assets[index];
                  return _AssetListItem(asset: asset);
                },
                childCount: _assets.length,
              ),
            ),
          ),

          // Bottom padding for FAB
          const SliverToBoxAdapter(
            child: SizedBox(height: 80),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // TODO: Navigate to add asset screen
        },
        icon: const Icon(Icons.add),
        label: const Text('Varlık Ekle'),
      ),
    );
  }

  Widget _buildPortfolioOverview(ThemeData theme, bool isTablet) {
    final isPositive = widget.portfolio['dailyChange'] >= 0;
    final changeColor = isPositive ? Colors.green[600] : Colors.red[600];

    return Container(
      margin: EdgeInsets.all(isTablet ? 24.0 : 16.0),
      padding: const EdgeInsets.all(20.0),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primaryContainer,
            theme.colorScheme.secondaryContainer,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Portföy Değeri',
            style: theme.textTheme.titleMedium?.copyWith(
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '₺${widget.portfolio['totalValue'].toStringAsFixed(2)}',
            style: theme.textTheme.displayMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Icon(
                isPositive ? Icons.trending_up : Icons.trending_down,
                color: changeColor,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                '${isPositive ? '+' : ''}₺${widget.portfolio['dailyChange'].toStringAsFixed(2)}',
                style: TextStyle(
                  color: changeColor,
                  fontWeight: FontWeight.w600,
                  fontSize: 18,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '(${isPositive ? '+' : ''}${widget.portfolio['dailyChangePercent'].toStringAsFixed(1)}%)',
                style: TextStyle(
                  color: changeColor,
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _StatItem(
                label: 'Varlık',
                value: '${widget.portfolio['assetCount']}',
                icon: Icons.account_balance_wallet_outlined,
              ),
              _StatItem(
                label: 'İşlem',
                value: '24',
                icon: Icons.swap_horiz,
              ),
              _StatItem(
                label: 'Kar/Zarar',
                value: '+₺5,234',
                icon: Icons.trending_up,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceChart(ThemeData theme, bool isTablet) {
    return Container(
      margin: EdgeInsets.symmetric(
        horizontal: isTablet ? 24.0 : 16.0,
        vertical: 16.0,
      ),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Performans',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(value: '1D', label: Text('1G')),
                      ButtonSegment(value: '1W', label: Text('1H')),
                      ButtonSegment(value: '1M', label: Text('1A')),
                      ButtonSegment(value: '1Y', label: Text('1Y')),
                    ],
                    selected: {'1W'},
                    onSelectionChanged: (Set<String> newSelection) {},
                  ),
                ],
              ),
              const SizedBox(height: 20),
              // Placeholder for chart
              Container(
                height: 200,
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceVariant.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.show_chart,
                        size: 48,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Grafik Yakında Eklenecek',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showMoreOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.share_outlined),
                title: const Text('Paylaş'),
                onTap: () {
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.download_outlined),
                title: const Text('Rapor İndir'),
                onTap: () {
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete_outline),
                title: const Text('Portföyü Sil'),
                onTap: () {
                  Navigator.pop(context);
                },
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _StatItem({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Icon(
          icon,
          size: 24,
          color: theme.colorScheme.primary,
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onPrimaryContainer,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onPrimaryContainer.withOpacity(0.7),
          ),
        ),
      ],
    );
  }
}

class _AssetListItem extends StatelessWidget {
  final Map<String, dynamic> asset;

  const _AssetListItem({required this.asset});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isProfit = asset['profitLoss'] >= 0;
    final profitColor = isProfit ? Colors.green[600] : Colors.red[600];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: CircleAvatar(
          backgroundColor: theme.colorScheme.primaryContainer,
          child: Text(
            asset['symbol'].substring(0, 1),
            style: TextStyle(
              color: theme.colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          asset['symbol'],
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(asset['name']),
            const SizedBox(height: 4),
            Text(
              '${asset['quantity']} adet × ₺${asset['currentPrice'].toStringAsFixed(2)}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
        trailing: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '₺${asset['totalValue'].toStringAsFixed(2)}',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  isProfit ? Icons.arrow_upward : Icons.arrow_downward,
                  size: 14,
                  color: profitColor,
                ),
                const SizedBox(width: 4),
                Text(
                  '${isProfit ? '+' : ''}${asset['profitLossPercent'].toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: profitColor,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
        onTap: () {
          // TODO: Navigate to asset detail
        },
      ),
    );
  }
}
