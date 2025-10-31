import 'package:flutter/material.dart';
import 'package:spsschool/routes/app_routes.dart';
import 'pages/treinamentos.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SPSSchool',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: AppRoutes.login,
      routes: AppRoutes.routes,
      onGenerateRoute: (settings) {
        // Primeiro tenta as rotas do AppRoutes
        final route = AppRoutes.generateRoute(settings);
        if (route != null) return route;

        // Depois trata as rotas específicas
        if (settings.name == '/treinamentos') {
          final args = settings.arguments as Map<String, dynamic>;
          final moduloId = args['moduloId'] as int;
          return MaterialPageRoute(
            builder: (_) => TreinamentosPage(moduloId: moduloId),
          );
        }
        return null;
      },
    );
  }
}