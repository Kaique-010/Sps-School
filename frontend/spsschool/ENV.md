Configuração de BASE_URL (ambientes)
===================================

Este projeto centraliza a URL da API em `lib/config/backend.dart` usando `String.fromEnvironment`.

Defina a variável em tempo de build/run com `--dart-define=BASE_URL=<url>`.

Exemplos:

- Desenvolvimento (emulador Android):
  - `flutter run --dart-define=BASE_URL=http://10.0.2.2:8000`
- Desenvolvimento (dispositivo físico na mesma rede):
  - `flutter run --dart-define=BASE_URL=http://SEU_IP_LOCAL:8000`
- Web (Chrome):
  - `flutter run -d chrome --dart-define=BASE_URL=http://localhost:8000`
- Produção (APK release):
  - `flutter build apk --release --dart-define=BASE_URL=https://sps-training.site`

Padrão
------
Se `BASE_URL` não for informado, o padrão é `http://localhost:8000` (definido em `Backend.baseUrl`).

Onde é usado
------------
- `ApiService` (login): usa `Backend.baseUrl`
- `ModuloService` (módulos/treinamentos): instanciado em `TreinamentosPage` e `DynamicDrawerWidget` usando `Backend.baseUrl`