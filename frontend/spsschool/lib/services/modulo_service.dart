import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ModuloService {
  final String baseUrl;

  ModuloService({required this.baseUrl});

  Future<List<dynamic>> listarModulos() async {
    final url = Uri.parse('$baseUrl/api/treinamentos/modulos/');
    final headers = await _authHeaders();
    final res = await http.get(url, headers: headers);
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      // A API retorna um objeto paginado, então pegamos apenas os results
      return data['results'] ?? [];
    } else {
      throw Exception('Erro ao buscar módulos');
    }
  }

  Future<List<dynamic>> listarTreinamentos(int moduloId) async {
    final url = Uri.parse('$baseUrl/api/treinamentos/?modulo=$moduloId');
    final headers = await _authHeaders();
    final res = await http.get(url, headers: headers);
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      // A API retorna um objeto paginado, então pegamos apenas os results
      return data['results'] ?? [];
    } else {
      throw Exception('Erro ao buscar treinamentos');
    }
  }

  Future<Map<String, String>> _authHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }
}
