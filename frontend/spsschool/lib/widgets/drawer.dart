import 'package:flutter/material.dart';

class DrawerWidget extends StatelessWidget {
  const DrawerWidget({super.key});

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
            child: ListView(
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

                _buildExpansionMenu(
                context,
                icon: Icons.folder_rounded,
                title: 'Cadastros',
                items: [
                  {'label': 'Treinamentos de Cadastros', 'moduloId': '1'},
                ],
              ),
              _buildExpansionMenu(
                context,
                icon: Icons.inventory_rounded,
                title: 'Estoque',
                items: [
                  {'label': 'Treinamentos de Estoque geral', 'moduloId': '2'},
                ],
              ),
              _buildExpansionMenu(
                context,
                icon: Icons.attach_money_rounded,
                title: 'Financeiro',
                items: [
                  {'label': 'Treinamentos de Financeiro', 'moduloId': '3'},
                ],
              ),
              _buildExpansionMenu(
                context,
                icon: Icons.shopping_cart_rounded,
                title: 'Vendas e Saídas',
                items: [
                  {'label': 'Treinamentos de Vendas e Saídas', 'moduloId': '4'},
                ],
              ),

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

  Widget _buildExpansionMenu(
  BuildContext context, {
  required IconData icon,
  required String title,
  required List<Map<String, String>> items,
}) {
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
          child: Icon(icon, size: 22, color: const Color(0xFFFFA601)),
        ),
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 15,
            fontWeight: FontWeight.w500,
          ),
        ),
        iconColor: const Color(0xFFFFA601),
        collapsedIconColor: Colors.white60,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        collapsedShape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        children: items.map((item) {
          return _buildSubMenuItem(
            context,
            label: item['label']!,
            moduloId: int.parse(item['moduloId']!),
          );
        }).toList(),
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
            Text(
              label,
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 14,
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