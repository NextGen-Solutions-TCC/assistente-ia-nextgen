from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction

from allauth.account.models import EmailAddress

from .models import Usuario, Conversa, Mensagem, ModeloIA


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = '__all__'


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

        validate_password(value)

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
        nome = validated_data.pop('nome', username)

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
    