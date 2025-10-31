from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer para autenticação de usuário
    """
    username = serializers.CharField(
        max_length=150,
        help_text="Nome de usuário"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Senha do usuário"
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciais inválidas. Verifique seu usuário e senha.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Conta de usuário desativada.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Deve incluir "username" e "password".',
                code='authorization'
            )


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para dados do usuário
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login'
        ]


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil completo do usuário
    """
    nome_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nome_completo',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'username',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login'
        ]
    
    def get_nome_completo(self, obj):
        """
        Retorna o nome completo do usuário
        """
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username