import 'package:flutter/material.dart';
import 'package:spsschool/widgets/dynamic_drawer.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1C1B),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color.fromARGB(255, 19, 66, 58),
        
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          const SizedBox(width: 8),
        ],
      ),
      drawer: const DynamicDrawerWidget(),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Banner de boas-vindas
            Container(
              width: double.infinity,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color.fromARGB(255, 12, 36, 32),
                    Color.fromARGB(255, 48, 121, 109),
                  ],
                ),
              ),
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(32.0),
                    child: Column(
                      children: [
                        Image.asset(
                          'images/logo.png',
                          width: 90,
                          height: 100,
                          fit: BoxFit.contain,
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'Bem-vindo ao Spartacus Training!',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        
                      ],
                    ),
                  ),
                  Container(
                    height: 30,
                    decoration: const BoxDecoration(
                      color: Color(0xFF1A1C1B),
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(30),
                        topRight: Radius.circular(30),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Cards de acesso rápido
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Acesso Rápido',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Grid de cards
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      _buildQuickAccessCard(
                        context,
                        icon: Icons.people_rounded,
                        title: 'Cadastros',
                        subtitle: 'Cadastros em Geral',
                        color: const Color(0xFF4A90E2),
                        route: '/cadastros',
                      ),
                      _buildQuickAccessCard(
                        context,
                        icon: Icons.inventory_rounded,
                        title: 'Estoque',
                        subtitle: 'Controles para estoque em geral',
                        color: const Color(0xFF9B59B6),
                        route: '/estoque',
                      ),
                      _buildQuickAccessCard(
                        context,
                        icon: Icons.payment_rounded,
                        title: 'Financeiro',
                        subtitle: 'Visualizar controles financeiros',
                        color: const Color(0xFFFFA601),
                        route: '/pagar',
                      ),
                      _buildQuickAccessCard(
                        context,
                        icon: Icons.shopping_cart_rounded,
                        title: 'Vendas e Saídas',
                        subtitle: 'Administrar vendas e saídas',
                        color: const Color(0xFF276359),
                        route: '/vendas',
                      ),
                    ],
                  ),

                  const SizedBox(height: 32),

                  // Seção de estatísticas
                  const Text(
                    'Visão Geral',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),

                  _buildStatCard(
                    icon: Icons.trending_up_rounded,
                    title: '',
                    value: '',
                    color: Colors.green,
                  ),
                  const SizedBox(height: 12),
                  _buildStatCard(
                    icon: Icons.group_rounded,
                    title: 'Alunos Ativos',
                    value: '1',
                    color: const Color(0xFF4A90E2),
                  ),
                  const SizedBox(height: 12),
                  _buildStatCard(
                    icon: Icons.calendar_today_rounded,
                    title: 'Treinamentos Aplicados',
                    value: '',
                    color: const Color(0xFFFFA601),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAccessCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required String route,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () {
          Navigator.pushNamed(context, route);
        },
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF2A2C2B),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.white.withOpacity(0.1),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.1),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    icon,
                    size: 32,
                    color: color,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.6),
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2C2B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: color,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}