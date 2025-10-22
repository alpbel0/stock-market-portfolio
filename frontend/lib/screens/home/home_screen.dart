import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const DashboardTab(),
    const PortfolioTab(),
    const MarketTab(),
    const ProfileTab(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isTablet = MediaQuery.of(context).size.width >= 600;
    
    return Scaffold(
      appBar: AppBar(
        title: Text(_getTitle(_selectedIndex)),
        actions: [
          // Notifications
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              // TODO: Navigate to notifications
            },
          ),
          // User profile avatar
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: CircleAvatar(
              backgroundColor: theme.colorScheme.primaryContainer,
              child: Icon(
                Icons.person_outline,
                color: theme.colorScheme.onPrimaryContainer,
              ),
            ),
          ),
        ],
      ),
      drawer: !isTablet ? _buildDrawer(context, theme) : null,
      body: SafeArea(
        child: isTablet
            ? Row(
                children: [
                  NavigationRail(
                    selectedIndex: _selectedIndex,
                    onDestinationSelected: _onItemTapped,
                    labelType: NavigationRailLabelType.all,
                    destinations: const [
                      NavigationRailDestination(
                        icon: Icon(Icons.dashboard_outlined),
                        selectedIcon: Icon(Icons.dashboard),
                        label: Text('Ana Sayfa'),
                      ),
                      NavigationRailDestination(
                        icon: Icon(Icons.account_balance_wallet_outlined),
                        selectedIcon: Icon(Icons.account_balance_wallet),
                        label: Text('Portföy'),
                      ),
                      NavigationRailDestination(
                        icon: Icon(Icons.trending_up_outlined),
                        selectedIcon: Icon(Icons.trending_up),
                        label: Text('Piyasa'),
                      ),
                      NavigationRailDestination(
                        icon: Icon(Icons.person_outline),
                        selectedIcon: Icon(Icons.person),
                        label: Text('Profil'),
                      ),
                    ],
                  ),
                  const VerticalDivider(thickness: 1, width: 1),
                  Expanded(child: _screens[_selectedIndex]),
                ],
              )
            : _screens[_selectedIndex],
      ),
      bottomNavigationBar: !isTablet
          ? NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: _onItemTapped,
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.dashboard_outlined),
                  selectedIcon: Icon(Icons.dashboard),
                  label: 'Ana Sayfa',
                ),
                NavigationDestination(
                  icon: Icon(Icons.account_balance_wallet_outlined),
                  selectedIcon: Icon(Icons.account_balance_wallet),
                  label: 'Portföy',
                ),
                NavigationDestination(
                  icon: Icon(Icons.trending_up_outlined),
                  selectedIcon: Icon(Icons.trending_up),
                  label: 'Piyasa',
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person),
                  label: 'Profil',
                ),
              ],
            )
          : null,
    );
  }

  String _getTitle(int index) {
    switch (index) {
      case 0:
        return 'Ana Sayfa';
      case 1:
        return 'Portföy';
      case 2:
        return 'Piyasa';
      case 3:
        return 'Profil';
      default:
        return 'Portfolio App';
    }
  }

  Widget _buildDrawer(BuildContext context, ThemeData theme) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                CircleAvatar(
                  radius: 32,
                  backgroundColor: theme.colorScheme.primary,
                  child: Icon(
                    Icons.person,
                    size: 32,
                    color: theme.colorScheme.onPrimary,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Kullanıcı Adı',
                  style: theme.textTheme.titleLarge?.copyWith(
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
                Text(
                  'user@example.com',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onPrimaryContainer.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard_outlined),
            title: const Text('Ana Sayfa'),
            onTap: () {
              Navigator.pop(context);
              setState(() {
                _selectedIndex = 0;
              });
            },
          ),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet_outlined),
            title: const Text('Portföyüm'),
            onTap: () {
              Navigator.pop(context);
              setState(() {
                _selectedIndex = 1;
              });
            },
          ),
          ListTile(
            leading: const Icon(Icons.trending_up_outlined),
            title: const Text('Piyasa'),
            onTap: () {
              Navigator.pop(context);
              setState(() {
                _selectedIndex = 2;
              });
            },
          ),
          ListTile(
            leading: const Icon(Icons.analytics_outlined),
            title: const Text('İstatistikler'),
            onTap: () {
              Navigator.pop(context);
              // TODO: Navigate to statistics
            },
          ),
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('İşlem Geçmişi'),
            onTap: () {
              Navigator.pop(context);
              // TODO: Navigate to transaction history
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: const Text('Ayarlar'),
            onTap: () {
              Navigator.pop(context);
              // TODO: Navigate to settings
            },
          ),
          ListTile(
            leading: const Icon(Icons.help_outline),
            title: const Text('Yardım'),
            onTap: () {
              Navigator.pop(context);
              // TODO: Navigate to help
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Çıkış Yap'),
            onTap: () {
              // TODO: Implement logout
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }
}

// Tab Screens
class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = screenWidth >= 600;
    final crossAxisCount = isTablet ? 2 : 1;
    
    return SingleChildScrollView(
      padding: EdgeInsets.all(isTablet ? 24.0 : 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Portfolio Summary Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Toplam Portföy Değeri',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '₺125,430.50',
                    style: Theme.of(context).textTheme.displayMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.trending_up,
                        color: Colors.green[600],
                        size: 20,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '+2,450.30 (2.0%)',
                        style: TextStyle(
                          color: Colors.green[600],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // Quick Actions
          Text(
            'Hızlı İşlemler',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.add,
                  label: 'Al',
                  color: Colors.green,
                  onTap: () {},
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.remove,
                  label: 'Sat',
                  color: Colors.red,
                  onTap: () {},
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Recent Activities
          Text(
            'Son İşlemler',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: 5,
            itemBuilder: (context, index) {
              return ListTile(
                leading: const CircleAvatar(
                  child: Icon(Icons.trending_up),
                ),
                title: Text('İşlem ${index + 1}'),
                subtitle: const Text('Bugün, 14:30'),
                trailing: const Text(
                  '+₺1,234.56',
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(icon, size: 32, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class PortfolioTab extends StatelessWidget {
  const PortfolioTab({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Portföy Ekranı - Yakında'),
    );
  }
}

class MarketTab extends StatelessWidget {
  const MarketTab({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Piyasa Ekranı - Yakında'),
    );
  }
}

class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Profil Ekranı - Yakında'),
    );
  }
}