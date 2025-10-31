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
