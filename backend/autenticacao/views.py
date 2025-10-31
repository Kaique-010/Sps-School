from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import LoginSerializer, UsuarioSerializer, UsuarioPerfilSerializer


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
