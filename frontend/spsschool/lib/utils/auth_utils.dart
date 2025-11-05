// lib/utils/auth_utils.dart
import 'package:shared_preferences/shared_preferences.dart';

/// Recupera o token JWT salvo após o login
Future<String?> getAuthToken() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString('access_token');
}
