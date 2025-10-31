import 'package:flutter/material.dart';
import '../services/modulo_service.dart';
import 'video_page.dart';

class TreinamentosPage extends StatelessWidget {
  final int moduloId;
  const TreinamentosPage({super.key, required this.moduloId});

  @override
  Widget build(BuildContext context) {
    final service = ModuloService(baseUrl: 'http://localhost:8000');

    return Scaffold(
      appBar: AppBar(title: const Text('Treinamentos')),
      body: FutureBuilder<List<dynamic>>(
        future: service.listarTreinamentos(moduloId),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final treinamentos = snapshot.data!;
          return ListView.builder(
            itemCount: treinamentos.length,
            itemBuilder: (_, i) {
              final t = treinamentos[i];
              return ListTile(
                title: Text(t['titulo']),
                subtitle: Text(t['conteudo'] ?? ''),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => VideoPage(
                        videoUrl: t['video_url'],
                        treinamentoId: t['id'],
                      ),
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}
