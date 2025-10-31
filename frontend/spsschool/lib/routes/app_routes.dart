import 'package:flutter/material.dart';
import '../pages/login_page.dart';  
import '../pages/home_page.dart';
import '../pages/video_page.dart';

class AppRoutes {
  static const login = '/login';
  static const home = '/home';
  static const video = '/video';

  static Map<String, WidgetBuilder> routes = {
    login: (_) => const LoginPage(),
    home: (_) => const HomePage(),
  };

  static Route<dynamic>? generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case video:
        final args = settings.arguments as Map<String, dynamic>;
        return MaterialPageRoute(
          builder: (_) => VideoPage(
            videoUrl: args['videoUrl'] as String,
            treinamentoId: args['treinamentoId'] as int,
          ),
        );
      default:
        return null;
    }
  }
}
