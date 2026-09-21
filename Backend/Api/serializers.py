from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction

from rest_framework import serializers

from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from dj_rest_auth.serializers import PasswordResetSerializer

from .models import Conversa, Mensagem, ModeloIA, Usuario

FRONTEND_URL = "http://localhost:5173"


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = '__all__'


class PerfilSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nome',
            'email',
            'tipo',
            'data_criacao',
        ]
        read_only_fields = [
            'id',
            'email',
            'tipo',
            'data_criacao',
        ]


class RegisterSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirmar_password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'confirmar_password',
            'nome',
        ]

    def validate_email(self, value):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Este email já está cadastrado."
            )

        return value

    def validate_password(self, value):

        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                list(exc.messages)
            )

        return value

    def validate(self, data):

        if data['password'] != data['confirmar_password']:
            raise serializers.ValidationError({
                "password": "As senhas não coincidem."
            })

        return data

    def create(self, validated_data):

        validated_data.pop('confirmar_password')

        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        nome = validated_data.pop('nome')

        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                usuario = Usuario.objects.create(
                    user=user,
                    nome=nome,
                    email=email
                )

                email_address = EmailAddress.objects.create(
                    user=user,
                    email=email,
                    primary=True,
                    verified=False
                )

                request = self.context.get('request')
                transaction.on_commit(
                    lambda: email_address.send_confirmation(request, signup=True)
                )

        except IntegrityError:
            raise serializers.ValidationError(
                "Não foi possível criar o usuário. "
                "Nome de usuário ou email já em uso."
            )

        return usuario


class ModeloIASerializer(serializers.ModelSerializer):

    class Meta:
        model = ModeloIA
        fields = '__all__'


class ConversaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversa
        fields = '__all__'
        read_only_fields = ['Id_usuario']


class MensagemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mensagem
        fields = '__all__'


def _frontend_password_reset_url_generator(request, user, temp_key):
    """
    Faz o e-mail de "esqueci minha senha" apontar para o React (que tem a
    tela de redefinição) em vez da rota padrão do dj-rest-auth, que aponta
    para o backend Django (sem template para renderizar).
    """
    uid = user_pk_to_url_str(user)
    return f"{FRONTEND_URL}/redefinir-senha/{uid}/{temp_key}/"


class CustomPasswordResetSerializer(PasswordResetSerializer):

    def get_email_options(self):
        return {'url_generator': _frontend_password_reset_url_generator}