import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:spsschool/config/backend.dart';

// Import condicional para Web
import '../utils/web_utils.dart' if (dart.library.io) '../utils/mobile_utils.dart';

class VideoPage extends StatefulWidget {
  final String videoUrl;
  final int treinamentoId;
  final String? treinamentoConteudo;

  const VideoPage({
    super.key,
    required this.videoUrl,
    required this.treinamentoId,
    this.treinamentoConteudo,
  });

  @override
  State<VideoPage> createState() => _VideoPageState();
}

class _VideoPageState extends State<VideoPage> {
  bool _isPlayerReady = false;
  String? _videoId;
  YoutubePlayerController? _ytController;
  String? _conteudo;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  void _initializePlayer() {
    // Extrair o ID do vídeo da URL do YouTube
    _videoId = _extractVideoId(widget.videoUrl);
    
    if (_videoId != null) {
      if (!kIsWeb) {
        _ytController = YoutubePlayerController(
          initialVideoId: _videoId!,
          flags: const YoutubePlayerFlags(
            autoPlay: false,
            mute: false,
            enableCaption: true,
            controlsVisibleAtStart: true,
          ),
        );
      }
      setState(() {
        _isPlayerReady = true;
      });
    }
  }

  String? _extractVideoId(String url) {
    // Extrair ID do vídeo de diferentes formatos de URL do YouTube
    RegExp regExp = RegExp(
      r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
      caseSensitive: false,
      multiLine: false,
    );
    
    final match = regExp.firstMatch(url);
    return match?.group(1);
  }

  @override
  void dispose() {
    _ytController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vídeo do Treinamento'),
        backgroundColor: const Color(0xFF1A1C1B),
        foregroundColor: Colors.white,
      ),
      backgroundColor: const Color(0xFF1A1C1B),
      body: _videoId != null
          ? SingleChildScrollView(
              child: Column(
                children: [
                  // Player de vídeo
                  Container(
                    margin: const EdgeInsets.all(16),
                    height: 250,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.3),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: _buildYouTubePlayer(),
                    ),
                  ),

                  // Controles personalizados
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2C2B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildControlButton(
                          icon: Icons.replay_10,
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Use os controles do player para navegar'),
                                backgroundColor: Color(0xFFFFA601),
                              ),
                            );
                          },
                        ),
                        _buildControlButton(
                          icon: Icons.play_arrow,
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Use os controles do player para reproduzir'),
                                backgroundColor: Color(0xFFFFA601),
                              ),
                            );
                          },
                          isMain: true,
                        ),
                        _buildControlButton(
                          icon: Icons.forward_10,
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Use os controles do player para navegar'),
                                backgroundColor: Color(0xFFFFA601),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Conteúdo do treinamento
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2C2B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Conteúdo',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        FutureBuilder<void>(
                          future: _ensureConteudoLoaded(),
                          builder: (context, snapshot) {
                            if (_conteudo == null && snapshot.connectionState != ConnectionState.done) {
                              return Text(
                                'Carregando conteúdo...',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.8),
                                  fontSize: 14,
                                ),
                              );
                            }
                            final texto = _conteudo ?? 'Sem conteúdo disponível';
                            return Text(
                              texto,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Informações do treinamento
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2C2B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Informações do Treinamento',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'ID do Treinamento: ${widget.treinamentoId}',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'URL do Vídeo: ${widget.videoUrl}',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Status: ${_isPlayerReady ? "Pronto para reprodução" : "Carregando..."}',
                          style: TextStyle(
                            color: _isPlayerReady 
                                ? const Color(0xFFFFA601)
                                : Colors.white.withOpacity(0.6),
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),
                ],
              ),
            )
          : Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.red.withOpacity(0.7),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'URL de vídeo inválida',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Não foi possível carregar o vídeo',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildYouTubePlayer() {
    if (_videoId == null) {
      return Container(
        color: Colors.black,
        child: const Center(
          child: Text(
            'Erro ao carregar vídeo',
            style: TextStyle(color: Colors.white),
          ),
        ),
      );
    }

    // Implementação condicional por plataforma
    if (kIsWeb) {
      return _buildWebYouTubePlayer();
    } else {
      return _buildMobileYouTubePlayer();
    }
  }

  Widget _buildWebYouTubePlayer() {
    // Registrar o view factory para o iframe (apenas Web)
    final String viewId = 'youtube-player-$_videoId';
    
    // Usar WebUtils para registrar o view factory
    WebUtils.registerYouTubeViewFactory(viewId, _videoId!);

    return HtmlElementView(viewType: viewId);
  }

  Widget _buildMobileYouTubePlayer() {
    if (_ytController == null) {
      return Container(
        color: Colors.black,
        child: const Center(
          child: Text(
            'Player indisponível',
            style: TextStyle(color: Colors.white),
          ),
        ),
      );
    }
    return YoutubePlayer(
      controller: _ytController!,
      showVideoProgressIndicator: true,
      progressIndicatorColor: const Color(0xFFFFA601),
      progressColors: const ProgressBarColors(
        playedColor: Color(0xFFFFA601),
        handleColor: Color(0xFFFFA601),
        backgroundColor: Colors.white24,
        bufferedColor: Colors.white38,
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required VoidCallback onPressed,
    bool isMain = false,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: isMain 
            ? const Color(0xFFFFA601) 
            : Colors.white.withOpacity(0.1),
        shape: BoxShape.circle,
      ),
      child: IconButton(
        onPressed: onPressed,
        icon: Icon(
          icon,
          color: isMain ? Colors.black : Colors.white,
          size: isMain ? 32 : 24,
        ),
      ),
    );
  }

  Future<void> _ensureConteudoLoaded() async {
    // Se já temos conteúdo vindo da navegação, usa-o e não carrega de novo
    if (_conteudo != null) return;
    if (widget.treinamentoConteudo != null && widget.treinamentoConteudo!.isNotEmpty) {
      setState(() {
        _conteudo = widget.treinamentoConteudo;
      });
      return;
    }
    // Caso contrário, busca do backend pelo ID
    try {
      final url = Uri.parse('${Backend.baseUrl}/api/treinamentos/treinamentos/${widget.treinamentoId}/');
      final res = await http.get(url);
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        setState(() {
          _conteudo = (data['conteudo'] as String?) ?? '';
        });
      }
    } catch (_) {
      // Silencia erros de rede, mostra conteúdo vazio
      setState(() {
        _conteudo = _conteudo ?? '';
      });
    }
  }
}