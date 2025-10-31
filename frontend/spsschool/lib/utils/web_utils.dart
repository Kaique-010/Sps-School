// Utilitários específicos para Web
// ignore_for_file: avoid_web_libraries_in_flutter

import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

class WebUtils {
  static void registerYouTubeViewFactory(String viewId, String videoId) {
    ui_web.platformViewRegistry.registerViewFactory(
      viewId,
      (int viewId) {
        final iframe = html.IFrameElement()
          ..src = 'https://www.youtube.com/embed/$videoId?enablejsapi=1&origin=${html.window.location.origin}'
          ..style.border = 'none'
          ..style.width = '100%'
          ..style.height = '100%'
          ..allowFullscreen = true;
        
        return iframe;
      },
    );
  }
}