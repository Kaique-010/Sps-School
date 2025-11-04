Iniciando um projeto com Flutter:

flutter create spsschool

adiciona as dependencias http e shared_preferences

  http: ^1.2.0
  shared_preferences: ^2.2.0

e faz a primeira pub do app

flutter pub get


a Estrutura básicade um projeto com fluter tem a mesma ideia dos projetos componentizados REact 

lib/
 ├── main.dart              # equivale ao App.js
 ├── routes/
 │    ├── app_routes.dart   # nomes e paths das telas
 │    └── app_pages.dart    # lista de rotas + builders
 ├── pages/
 │    ├── login_page.dart
 │    ├── home_page.dart
 │    └── perfil_page.dart
 └── widgets/
      └── custom_drawer.dart


No Dart são usados Widgets, que são os seus componentes básicos, como AppBar, Scaffold, Center, Text, etc.

AppBar é um widget que é usado para criar uma barra de aplicativo, comum em muitos aplicativos Flutter.
Scaffold é um widget que é usado para criar a estrutura básica de uma tela, como a barra de aplicativo, o corpo da tela e o drawer.
Center é um widget que é usado para centralizar um widget filho.
Text é um widget que é usado para exibir texto.

para criar um drawer iremos usar o scaffold, e dentro do body, iremos usar o drawer.
Drawer é um widget que é usado para criar um menu lateral, comum em muitos aplicativos Flutter.
Drawer é composto por vários widgets, como ListView, ListTile, etc.
ListView é um widget que é usado para exibir uma lista de itens.

exemplo de drawer:

scaffold(
  appBar: AppBar(
    title: const Text('Academia Spartacus'),
  ),
  drawer: Drawer(
    child: ListView(
      padding: EdgeInsets.zero,
      children: [
        const DrawerHeader(
          decoration: BoxDecoration(
            color: Colors.blue,
          ),
          child: Text('Menu'),
        ),
        ListTile(
          title: const Text('Home'),
          onTap: () {
            Navigator.pop(context);
          },
        ),
        ListTile(
          title: const Text('Perfil'),
          onTap: () {
            Navigator.pop(context);
          },
        ),
      ],
    ),
  ),
  body: const Center(
    child: Text('Bem-vindo à Academia Spartacus!'),
  ),
);



Resumo do app

Configuração de rota com a api Backend em django para o base em lib/config/backend.dart

dessa maneira todas as rotas do app serão prefixadas com /api e serão acessíveis através de http://localhost:8000/api/ ou através do site http://www.sps-training.site/api/

as paginas do app são criadas em lib/pages/

temos as seguintes paginas:

home_page.dart:

constando a página principal do aplicativo onde :

temos um drawer lateral com a sopções de direcionamento para os manuais de cada módulo

a página de login 

de treinamentos que funciona dinamicamente, com base na lista de treinamentos retornada pela api.
Nela constam o id, o nome do treinamento, o conteúdo, a duração e o link para o video.

e a de video que contém os videos de cada treinamento, também dinâmica, com base na lista de videos retornada pela api.



Em lib/routes temos as seguintes rotas:

app_routes.dart:

const String loginRoute = '/login';
const String homeRoute = '/home';
const String perfilRoute = '/perfil';
const String treinamentosRoute = '/treinamentos';
const String videoRoute = '/video';

cada uma delas é usada para direcionar para a respectiva página.

se for acrescentar mais rotas, basta adicionar no arquivo app_routes.dart e no arquivo app_pages.dart

em Services temos os seguintes arquivos:


api_service.dart:

contém as funções de comunicação com a api, como a requisição de treinamentos e videos.

para realizar o login e obter o token de acesso, usamos a função login()


e em libs/widgets/ temos os seguintes widgets:

custom_drawer.dart:

contém o drawer lateral com as opções de direcionamento para os manuais de cada módulo

e o main_drawer.dart:

Que funciona como App.json, contém o drawer principal



Paa finalizar o app, é necessário configurar o arquivo pubspec.yaml para adicionar as fontes e as imagens usadas no app.

Deploy (Android e iOS)

Android (Windows/macOS/Linux):
- Gere APK release: `flutter build apk --release --dart-define=BASE_URL=https://www.sps-training.site`
- Opcional: App Bundle para Play Store: `flutter build appbundle --release --dart-define=BASE_URL=https://www.sps-training.site`

iOS (somente macOS, com Xcode):
- Pré-requisitos: Xcode instalado, conta de desenvolvedor, CocoaPods (`sudo gem install cocoapods`), executar `pod install` dentro do diretório `ios/`.
- Abra `ios/Runner.xcworkspace` e configure em Signing & Capabilities:
  - `Team` (time de desenvolvimento)
  - `Bundle Identifier`
  - `Deployment Target` adequado
- Se usar HTTP em desenvolvimento, ajuste o `Info.plist` para permitir carregamentos (ATS). Exemplo:
  ```xml
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
  </dict>
  ```
  Em produção, prefira `https` e remova a exceção.
- Build para distribuição (IPA):
  - `flutter build ipa --release --dart-define=BASE_URL=https://www.sps-training.site`
  - Alternativamente, `flutter build ios --release` (gera o app e requer assinatura via Xcode para exportar IPA).

Observação: em Windows/Linux não é possível gerar iOS diretamente; use um Mac com Xcode para os comandos acima.

