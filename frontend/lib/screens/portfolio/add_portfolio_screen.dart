import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AddPortfolioScreen extends ConsumerStatefulWidget {
  final Map<String, dynamic>? portfolio;

  const AddPortfolioScreen({
    super.key,
    this.portfolio,
  });

  @override
  ConsumerState<AddPortfolioScreen> createState() =>
      _AddPortfolioScreenState();
}

class _AddPortfolioScreenState extends ConsumerState<AddPortfolioScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.portfolio != null) {
      _nameController.text = widget.portfolio!['name'];
      _descriptionController.text = widget.portfolio!['description'];
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  bool get isEditing => widget.portfolio != null;

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    if (mounted) {
      setState(() => _isLoading = false);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isEditing
                ? 'Portföy güncellendi'
                : 'Portföy oluşturuldu',
          ),
        ),
      );
      
      Navigator.pop(context);
    }
  }

  void _handleCancel() {
    if (_nameController.text.isEmpty && _descriptionController.text.isEmpty) {
      Navigator.pop(context);
      return;
    }

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Değişiklikleri İptal Et'),
        content: const Text(
          'Yaptığınız değişiklikler kaydedilmeyecek. Devam etmek istiyor musunuz?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Hayır'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Close screen
            },
            child: const Text('Evet'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isTablet = MediaQuery.of(context).size.width >= 600;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Portföyü Düzenle' : 'Yeni Portföy'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: _handleCancel,
        ),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: EdgeInsets.all(isTablet ? 24.0 : 16.0),
          children: [
            // Information Card
            Card(
              color: theme.colorScheme.primaryContainer,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: theme.colorScheme.onPrimaryContainer,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        isEditing
                            ? 'Portföy bilgilerinizi güncelleyin'
                            : 'Yeni bir portföy oluşturun ve varlıklarınızı takip edin',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Portfolio Name Field
            Text(
              'Portföy Adı *',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                hintText: 'Örn: Uzun Vadeli Yatırımlar',
                prefixIcon: const Icon(Icons.account_balance_wallet_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                helperText: 'Portföyünüz için açıklayıcı bir isim verin',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Portföy adı gereklidir';
                }
                if (value.trim().length < 3) {
                  return 'Portföy adı en az 3 karakter olmalıdır';
                }
                if (value.trim().length > 50) {
                  return 'Portföy adı en fazla 50 karakter olabilir';
                }
                return null;
              },
              textCapitalization: TextCapitalization.words,
              maxLength: 50,
            ),
            const SizedBox(height: 24),

            // Portfolio Description Field
            Text(
              'Açıklama',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _descriptionController,
              decoration: InputDecoration(
                hintText: 'Portföy hakkında kısa bir açıklama (opsiyonel)',
                prefixIcon: const Icon(Icons.description_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                helperText: 'Portföyünüzün amacını veya stratejisini açıklayın',
              ),
              maxLines: 3,
              maxLength: 200,
              textCapitalization: TextCapitalization.sentences,
              validator: (value) {
                if (value != null && value.trim().length > 200) {
                  return 'Açıklama en fazla 200 karakter olabilir';
                }
                return null;
              },
            ),
            const SizedBox(height: 24),

            // Portfolio Type (Optional)
            Text(
              'Portföy Tipi',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            _PortfolioTypeSelector(),
            const SizedBox(height: 32),

            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _isLoading ? null : _handleCancel,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('İptal'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: FilledButton(
                    onPressed: _isLoading ? null : _handleSave,
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          )
                        : Text(isEditing ? 'Güncelle' : 'Oluştur'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PortfolioTypeSelector extends StatefulWidget {
  @override
  State<_PortfolioTypeSelector> createState() => _PortfolioTypeSelectorState();
}

class _PortfolioTypeSelectorState extends State<_PortfolioTypeSelector> {
  String _selectedType = 'general';

  final List<Map<String, dynamic>> _portfolioTypes = [
    {
      'id': 'general',
      'label': 'Genel',
      'icon': Icons.account_balance_wallet_outlined,
    },
    {
      'id': 'stocks',
      'label': 'Hisse Senedi',
      'icon': Icons.trending_up,
    },
    {
      'id': 'crypto',
      'label': 'Kripto',
      'icon': Icons.currency_bitcoin,
    },
    {
      'id': 'retirement',
      'label': 'Emeklilik',
      'icon': Icons.savings_outlined,
    },
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: _portfolioTypes.map((type) {
        final isSelected = _selectedType == type['id'];
        return ChoiceChip(
          label: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                type['icon'],
                size: 18,
                color: isSelected
                    ? theme.colorScheme.onSecondaryContainer
                    : theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 8),
              Text(type['label']),
            ],
          ),
          selected: isSelected,
          onSelected: (selected) {
            setState(() {
              _selectedType = type['id'];
            });
          },
        );
      }).toList(),
    );
  }
}
