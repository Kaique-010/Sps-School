import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async'; // 🔹 Timer usado pra simular progresso no web
import 'package:spsschool/config/backend.dart';
import '../utils/auth_utils.dart';

// Import condicional para web e mobile (permite usar o mesmo widget nas duas plataformas)
import '../utils/web_utils.dart'
    if (dart.library.io) '../utils/mobile_utils.dart';

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
  bool _isPlayerReady = false; // controla se o player terminou de inicializar
  String? _videoId; // ID do vídeo extraído da URL do YouTube
  YoutubePlayerController? _ytController; // controlador do player (mobile)
  String? _conteudo; // conteúdo textual do treinamento
  double _progresso = 0.0; // 🔹 progresso atual (0 a 1)
  Timer?
  _timerWeb; // 🔹 simula progresso no navegador (pois o iframe não emite eventos)

  @override
  void initState() {
    super.initState();
    _initializePlayer(); // inicializa player e lógica de progresso
  }

  void _initializePlayer() {
    _videoId = _extractVideoId(widget.videoUrl); // extrai ID do YouTube

    if (_videoId != null) {
      if (kIsWeb) {
        // 🔹 Web: cria um timer que simula avanço no vídeo
        _timerWeb = Timer.periodic(const Duration(seconds: 5), (_) {
          if (_progresso < 1.0) {
            setState(() {
              _progresso += 0.05; // avança 5% a cada 5 segundos
              if (_progresso > 1.0) _progresso = 1.0; // limita a 100%
            });
            _enviarProgresso(_progresso); // envia progresso pro backend
          }
        });
      } else {
        // 🔹 Mobile: usa listener real do player
        _ytController =
            YoutubePlayerController(
              initialVideoId: _videoId!,
              flags: const YoutubePlayerFlags(
                autoPlay: false,
                mute: false,
                enableCaption: true,
                controlsVisibleAtStart: true,
              ),
            )..addListener(
              _listenerYoutube,
            ); // escuta posição do vídeo em tempo real
      }

      setState(() {
        _isPlayerReady = true;
      });
    }
  }

  /// 🔹 Listener do player (apenas mobile)
  void _listenerYoutube() async {
    if (!_isPlayerReady || _ytController == null) return;

    final posicao = _ytController!.value.position.inSeconds;
    final duracao = _ytController!.metadata.duration.inSeconds;
    if (duracao <= 0) return;

    final progresso = posicao / duracao; // calcula progresso entre 0–1
    setState(() => _progresso = progresso); // atualiza barra

    // Envia progresso a cada 10s ou ao atingir 95% do vídeo
    if (posicao % 10 == 0 || progresso >= 0.95) {
      await _enviarProgresso(progresso);
    }
  }

  /// 🔹 Envia progresso ao backend
  Future<void> _enviarProgresso(double progressoVideo) async {
    final token = await getAuthToken(); // 🔹 busca o token do login
    if (token == null) {
      debugPrint('❌ Nenhum token encontrado. Usuário não autenticado.');
      return;
    }

    final url = Uri.parse('${Backend.baseUrl}/api/treinamentos/progresso/');
    final body = jsonEncode({
      'treinamento': widget.treinamentoId,
      'progresso_video': progressoVideo,
      'lido': progressoVideo >= 0.95,
    });

    try {
      final res = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token', // 🔹 aqui está a mágica
        },
        body: body,
      );

      if (res.statusCode == 200 || res.statusCode == 201) {
        debugPrint(
          '✅ Progresso salvo: ${(progressoVideo * 100).toStringAsFixed(1)}%',
        );
      } else {
        debugPrint('⚠️ Erro ao salvar progresso: ${res.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Falha ao enviar progresso: $e');
    }
  }

  /// 🔹 Extrai o ID do vídeo (parte final da URL do YouTube)
  String? _extractVideoId(String url) {
    RegExp regExp = RegExp(
      r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
      caseSensitive: false,
    );
    return regExp.firstMatch(url)?.group(1);
  }

  @override
  void dispose() {
    // 🔹 encerra listeners e timers ao sair da tela
    _ytController?.removeListener(_listenerYoutube);
    _ytController?.dispose();
    _timerWeb?.cancel();
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
                  // 🔹 Player principal
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

                  // 🔹 Barra de progresso visual
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Column(
                      children: [
                        LinearProgressIndicator(
                          value: _progresso, // valor entre 0 e 1
                          backgroundColor: Colors.white24,
                          color: const Color(0xFFFFA601),
                          minHeight: 8,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          // exibe percentual formatado
                          '${(_progresso * 100).toStringAsFixed(1)}% concluído',
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // 🔹 Conteúdo textual do treinamento
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
                            if (_conteudo == null &&
                                snapshot.connectionState !=
                                    ConnectionState.done) {
                              return Text(
                                'Carregando conteúdo...',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.8),
                                  fontSize: 14,
                                ),
                              );
                            }
                            return Text(
                              _conteudo ?? 'Sem conteúdo disponível',
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
                ],
              ),
            )
          : const Center(
              child: Text(
                'Erro ao carregar vídeo',
                style: TextStyle(color: Colors.white),
              ),
            ),
    );
  }

  /// 🔹 Define o player dependendo da plataforma (web vs mobile)
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

    if (kIsWeb) {
      // 🔹 Web usa iframe HTML
      final String viewId = 'youtube-player-$_videoId';
      WebUtils.registerYouTubeViewFactory(viewId, _videoId!);
      return HtmlElementView(viewType: viewId);
    } else {
      // 🔹 Mobile usa plugin nativo
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
  }

  /// 🔹 Busca o conteúdo textual do backend (DRF)
  Future<void> _ensureConteudoLoaded() async {
    if (_conteudo != null) return;
    if (widget.treinamentoConteudo?.isNotEmpty == true) {
      setState(() => _conteudo = widget.treinamentoConteudo);
      return;
    }
    try {
      final url = Uri.parse(
        '${Backend.baseUrl}/api/treinamentos/treinamentos/${widget.treinamentoId}/',
      );
      final res = await http.get(url);
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        setState(() => _conteudo = (data['conteudo'] as String?) ?? '');
      }
    } catch (_) {
      setState(() => _conteudo = _conteudo ?? '');
    }
  }
}
