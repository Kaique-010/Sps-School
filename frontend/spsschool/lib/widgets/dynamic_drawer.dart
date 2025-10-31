import 'package:flutter/material.dart';
import '../services/modulo_service.dart';

class DynamicDrawerWidget extends StatefulWidget {
  const DynamicDrawerWidget({super.key});

  @override
  State<DynamicDrawerWidget> createState() => _DynamicDrawerWidgetState();
}

class _DynamicDrawerWidgetState extends State<DynamicDrawerWidget> {
  final ModuloService _moduloService = ModuloService(baseUrl: 'http://localhost:8000');
  List<dynamic> _modulos = [];
  bool _isLoading = true;
  String? _error;

  // Mapeamento de ícones para módulos
  final Map<String, IconData> _iconMap = {
    'cadastros': Icons.folder_rounded,
    'estoque': Icons.inventory_rounded,
    'financeiro': Icons.attach_money_rounded,
    'vendas': Icons.shopping_cart_rounded,
    'vendas e saídas': Icons.shopping_cart_rounded,
    'default': Icons.folder_rounded,
  };

  @override
  void initState() {
    super.initState();
    _carregarModulos();
  }

  Future<void> _carregarModulos() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });
      
      final modulos = await _moduloService.listarModulos();
      setState(() {
        _modulos = modulos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  IconData _getIconForModulo(String nomeModulo) {
    final nome = nomeModulo.toLowerCase();
    for (final key in _iconMap.keys) {
      if (nome.contains(key)) {
        return _iconMap[key]!;
      }
    }
    return _iconMap['default']!;
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: const Color(0xFF1A1C1B),
      child: Column(
        children: [
          // Header moderno com gradiente
          Container(
            height: 200,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color.fromARGB(255, 55, 143, 130),
                  Color.fromARGB(255, 15, 51, 45),
                ],
              ),
            ),
            child: Stack(
              children: [
                // Efeito de overlay
                Positioned.fill(
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withOpacity(0.1),
                        ],
                      ),
                    ),
                  ),
                ),
                // Conteúdo
                Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Image.asset(
                          'images/logo.png',
                          width: 40,
                          height: 60,
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            return const Icon(
                              Icons.school,
                              size: 40,
                              color: Colors.white,
                            );
                          },
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Spartacus',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Treinamentos de módulos Spartacus',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 13,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Lista de itens
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                      color: Color(0xFFFFA601),
                    ),
                  )
                : _error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.error_outline,
                              size: 48,
                              color: Colors.red.withOpacity(0.7),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'Erro ao carregar módulos',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.8),
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _error!,
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.6),
                                fontSize: 12,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _carregarModulos,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFFA601),
                                foregroundColor: Colors.black,
                              ),
                              child: const Text('Tentar Novamente'),
                            ),
                          ],
                        ),
                      )
                    : ListView(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        children: [
                          _buildMenuItem(
                            context,
                            icon: Icons.home_rounded,
                            title: 'Home',
                            route: '/home',
                          ),
                          
                          const SizedBox(height: 4),
                          _buildDivider(),
                          const SizedBox(height: 4),

                          // Módulos dinâmicos
                          ..._modulos.map((modulo) => _buildModuloExpansionMenu(
                                context,
                                modulo: modulo,
                              )),
                        ],
                      ),
          ),

          // Footer com logout
          _buildDivider(),
          _buildMenuItem(
            context,
            icon: Icons.logout_rounded,
            title: 'Sair',
            route: '/login',
            isLogout: true,
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String route,
    bool isLogout = false,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () {
            Navigator.pushReplacementNamed(context, route);
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isLogout
                        ? Colors.red.withOpacity(0.1)
                        : const Color(0xFFFFA601).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    size: 22,
                    color: isLogout
                        ? Colors.red.shade400
                        : const Color(0xFFFFA601),
                  ),
                ),
                const SizedBox(width: 16),
                Text(
                  title,
                  style: TextStyle(
                    color: isLogout ? Colors.red.shade400 : Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildModuloExpansionMenu(
    BuildContext context, {
    required Map<String, dynamic> modulo,
  }) {
    final moduloId = modulo['id'] as int;
    final moduloNome = modulo['nome'] as String;
    final moduloDescricao = modulo['descricao'] as String? ?? '';
    final treinamentos = modulo['treinamentos'] as List<dynamic>? ?? [];

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          leading: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFFFFA601).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              _getIconForModulo(moduloNome),
              size: 22,
              color: const Color(0xFFFFA601),
            ),
          ),
          title: Text(
            moduloNome,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 15,
              fontWeight: FontWeight.w500,
            ),
          ),
          subtitle: moduloDescricao.isNotEmpty
              ? Text(
                  moduloDescricao,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.6),
                    fontSize: 12,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                )
              : null,
          iconColor: const Color(0xFFFFA601),
          collapsedIconColor: Colors.white60,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          collapsedShape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          children: [
            _buildSubMenuItem(
              context,
              label: 'Treinamentos de $moduloNome',
              moduloId: moduloId,
            ),
            // Se houver treinamentos específicos, pode listar aqui
            if (treinamentos.isNotEmpty)
              ...treinamentos.take(3).map((treinamento) => _buildTreinamentoItem(
                    context,
                    treinamento: treinamento,
                    moduloId: moduloId,
                  )),
          ],
        ),
      ),
    );
  }

  Widget _buildSubMenuItem(
    BuildContext context, {
    required String label,
    required int moduloId,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/treinamentos',
            arguments: {'moduloId': moduloId},
          );
        },
        child: Container(
          padding: const EdgeInsets.only(left: 64, right: 16, top: 10, bottom: 10),
          child: Row(
            children: [
              Container(
                width: 4,
                height: 4,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFA601).withOpacity(0.6),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  label,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTreinamentoItem(
    BuildContext context, {
    required Map<String, dynamic> treinamento,
    required int moduloId,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          // Navegar diretamente para o vídeo do treinamento
          Navigator.pushNamed(
            context,
            '/video',
            arguments: {
              'videoUrl': treinamento['video_url'] ?? '',
              'treinamentoId': treinamento['id'],
            },
          );
        },
        child: Container(
          padding: const EdgeInsets.only(left: 80, right: 16, top: 8, bottom: 8),
          child: Row(
            children: [
              Icon(
                Icons.play_circle_outline,
                size: 16,
                color: const Color(0xFFFFA601).withOpacity(0.8),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  treinamento['titulo'] ?? 'Treinamento',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 12,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      height: 1,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.transparent,
            const Color(0xFFFFA601).withOpacity(0.3),
            Colors.transparent,
          ],
        ),
      ),
    );
  }
}