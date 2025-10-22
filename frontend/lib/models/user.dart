class User {
  final String id;
  final String email;
  final String? name;
  final DateTime createdAt;
  
  // Sentinel nesnesi: copyWith'ta 'parametre verilmedi' ile 'bilerek null verildi' ayrımını yapmak için
  static final Object _notProvided = Object();

  User({
    required this.id,
    required this.email,
    this.name,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      name: json['name'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'created_at': createdAt.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    Object? name = _notProvided,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: identical(name, _notProvided) ? this.name : name as String?,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
