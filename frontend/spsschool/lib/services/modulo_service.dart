import 'dart:convert';
import 'package:http/http.dart' as http;

class ModuloService {
  final String baseUrl;

  ModuloService({required this.baseUrl});

  Future<List<dynamic>> listarModulos() async {
    final url = Uri.parse('$baseUrl/api/treinamentos/modulos/');
    final res = await http.get(url);
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
    final res = await http.get(url);
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      // A API retorna um objeto paginado, então pegamos apenas os results
      return data['results'] ?? [];
    } else {
      throw Exception('Erro ao buscar treinamentos');
    }
  }
}
