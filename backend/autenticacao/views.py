from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect, render
from .serializers import LoginSerializer, UsuarioSerializer, UsuarioPerfilSerializer
from central_treinamentos.models import Modulo, Treinamento, ProgressoTreinamento


class LoginView(APIView):
    """
    View para autenticação de usuário e geração de tokens JWT
    """
    
    def post(self, request):
        """
        Autentica o usuário e retorna tokens JWT
        """
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Dados do usuário
            usuario_data = UsuarioSerializer(user).data
            
            return Response({
                'sucesso': True,
                'mensagem': 'Login realizado com sucesso',
                'dados': {
                    'usuario': usuario_data,
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh),
                    }
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'sucesso': False,
            'mensagem': 'Erro na autenticação',
            'erros': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginTemplateView(View):
    success_url = 'home.html'
    """
    View para renderizar o template de login (UI) na raiz
    """
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, 'login.html')

class LogoutTemplateView(View):
    success_url = 'login.html'
    """
    View para renderizar o template de logout (UI)
    """
    def get(self, request):
        return render(request, 'login.html')

class HomeView(View):
    """
    View para renderizar o template de home (UI)
    """
    def get(self, request):
        # Contagens gerais
        total_modulos = Modulo.objects.count()
        total_treinamentos = Treinamento.objects.count()

        # Progresso do usuário
        completed_treinamentos = 0
        total_certificates = 0
        if request.user.is_authenticated:
            completed_treinamentos = ProgressoTreinamento.objects.filter(
                usuario=request.user, lido=True
            ).count()
            # Sem model específico de certificados, usar concluídos como proxy
            total_certificates = completed_treinamentos

        context = {
            'modulos': Modulo.objects.prefetch_related('treinamentos').all(),
            'total_modulos': total_modulos,
            'total_treinamentos': total_treinamentos,
            'completed_treinamentos': completed_treinamentos,
            'total_certificates': total_certificates,
        }

        return render(request, 'home.html', context)

class SessionLoginView(APIView):
    """
    Autenticação baseada em sessão para a interface web.
    Cria a sessão do usuário (cookie) para que `request.user.is_authenticated` funcione nos templates.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({
                'sucesso': False,
                'mensagem': 'Informe usuário e senha.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({
                'sucesso': False,
                'mensagem': 'Credenciais inválidas.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({
            'sucesso': True,
            'mensagem': 'Login de sessão realizado com sucesso.'
        }, status=status.HTTP_200_OK)

class PerfilUsuarioView(RetrieveUpdateAPIView):
    """
    View para recuperar e atualizar dados do usuário autenticado
    """
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Retorna o usuário autenticado
        """
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """
        Recupera os dados do usuário autenticado
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'sucesso': True,
            'mensagem': 'Dados do usuário recuperados com sucesso',
            'dados': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Atualiza os dados do usuário autenticado
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'sucesso': True,
                'mensagem': 'Dados do usuário atualizados com sucesso',
                'dados': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'sucesso': False,
            'mensagem': 'Erro na atualização dos dados',
            'erros': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    View para logout do usuário (blacklist do refresh token)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Faz logout do usuário adicionando o refresh token à blacklist
        """
        try:
            refresh_token = request.data.get("refresh")
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return Response({
                    'sucesso': True,
                    'mensagem': 'Logout realizado com sucesso'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'sucesso': False,
                    'mensagem': 'Token de refresh é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'sucesso': False,
                'mensagem': 'Erro ao fazer logout',
                'erro': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class VerificarTokenView(APIView):
    """
    View para verificar se o token JWT é válido
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Verifica se o token é válido e retorna dados do usuário
        """
        usuario_data = UsuarioSerializer(request.user).data
        
        return Response({
            'sucesso': True,
            'mensagem': 'Token válido',
            'dados': {
                'usuario': usuario_data,
                'token_valido': True
            }
        }, status=status.HTTP_200_OK)
