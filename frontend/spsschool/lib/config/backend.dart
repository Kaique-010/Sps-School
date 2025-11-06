// Configuração centralizada de backend
// Use --dart-define=BASE_URL=<url> para definir em build/run

class Backend {
  // Não usar barra no final. Ex.: https://sps-training.site ou http://localhost:8000
  static const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
}
