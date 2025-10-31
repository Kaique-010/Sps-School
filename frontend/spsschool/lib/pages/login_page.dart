import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> with TickerProviderStateMixin {
  final TextEditingController _username = TextEditingController();
  final TextEditingController _password = TextEditingController();
  bool _loading = false;

  final ApiService api = ApiService(baseUrl: 'http://localhost:8000');

  // controllers de animação
  late AnimationController _logoController;
  late AnimationController _formController;
  late Animation<double> _logoOpacity;
  late Animation<Offset> _formSlide;

  @override
  void initState() {
    super.initState();

    _logoController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1300),
    );

    _formController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 850),
    );

    _logoOpacity = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _logoController, curve: Curves.easeOut),
    );

    _formSlide = Tween<Offset>(
      begin: const Offset(0, 0.7),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _formController, curve: Curves.easeOutCubic),
    );

    // dispara animações em sequência
    _logoController.forward().then((_) => _formController.forward());
  }

  @override
  void dispose() {
    _logoController.dispose();
    _formController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    setState(() => _loading = true);
    try {
      final data = await api.login(
        username: _username.text,
        password: _password.text,
      );

      if (data['sucesso'] == true && data['dados'] != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', data['dados']['tokens']['access']);
        await prefs.setString('username', data['dados']['usuario']['username']);
        Navigator.pushReplacementNamed(context, '/home');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Login realizado com sucesso!')),
        );
      } else {
        throw Exception(data['mensagem'] ?? 'Erro desconhecido');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF0E0E0E),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            padding: const EdgeInsets.all(24),
            width: size.width < 400 ? size.width * 0.9 : 400,
            decoration: BoxDecoration(
              color: const Color(0xFF1E1E1E),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Fade da logo
                FadeTransition(
                  opacity: _logoOpacity,
                  child: Image.asset(
                    'images/logo.png',
                    width: 90,
                    height: 100,
                    fit: BoxFit.contain,
                  ),
                ),

                const SizedBox(height: 16),

                const Text(
                  'Spartacus Training',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'Fauna',
                  ),
                ),

                const SizedBox(height: 32),

                // Slide do formulário
                SlideTransition(
                  position: _formSlide,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E1E),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        TextField(
                          controller: _username,
                          style: const TextStyle(color: Colors.white),
                          decoration: _inputStyle('Usuário'),
                        ),
                        const SizedBox(height: 16),
                        TextField(
                          controller: _password,
                          obscureText: true,
                          style: const TextStyle(color: Colors.white),
                          decoration: _inputStyle('Senha'),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // Botão animado com scale
                AnimatedScale(
                  scale: _loading ? 0.95 : 1.0,
                  duration: const Duration(milliseconds: 200),
                  child: _loading
                      ? const CircularProgressIndicator(
                          color: Color.fromARGB(255, 38, 62, 104),
                        )
                      : SizedBox(
                          width: double.infinity,
                          height: 50,
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  const Color.fromARGB(255, 20, 38, 70),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: _login,
                            child: const Text(
                              'Entrar',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputStyle(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: Colors.grey),
      filled: true,
      fillColor: const Color(0xFF2C2C2C),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Colors.blueAccent),
      ),
    );
  }
}
