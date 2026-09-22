from django.shortcuts import render, redirect
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework.decorators import action, permission_classes, api_view
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import urlencode


from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from django.core import signing
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account import app_settings as allauth_account_settings

FRONTEND_URL = "http://localhost:5173"

@receiver(user_logged_in)
def sinal_login_sucesso(sender, request, user, **kwargs):
    # Essa linha vai imprimir no terminal do VS Code sempre que alguém logar
    print(f"-------------------------------------------")
    print(f"SUCESSO: O usuário {user.email} acabou de entrar!")
    print(f"-------------------------------------------")


@api_view(['POST'])
def teste(request):
    print(f"DEBUG - Dados brutos: {request.data}") # Adicione esta linha!
    nome = request.data.get("nome")
    email = request.data.get("email")

    print(nome)
    print(email)

    return Response({
    "status": "sucesso",
        "mensagem": f"Usuário {nome} recebido!",
        "codigo": 200
})



class UsuarioViewSet(ModelViewSet): # viewset serve para criar as rotas automaticamente, não precisa criar uma view para cada ação
    queryset = Usuario.objects.all()# define a queryset para o viewset, ou seja, os dados que serão retornados quando uma requisição for feita para a rota do usuário. O queryset é uma forma de filtrar os dados que serão retornados, por exemplo, para retornar apenas os usuários ativos ou para retornar apenas os usuários com um determinado tipo.
    serializer_class = UsuarioSerializer
    # permission_classes = [IsAuthenticated]
 
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsuarioFilter
    
 
    def get_queryset(self): # def get_queryset(self) é um método que pode ser sobrescrito para personalizar a queryset retornada pelo viewset. No caso do usuário, queremos retornar apenas os dados do usuário logado, a menos que o usuário seja um superusuário (staff), nesse caso, ele pode ver todos os usuários.
        qs = super().get_queryset() # chama o método get_queryset() da classe pai (ModelViewSet) para obter a queryset padrão, que é definida como Usuario.objects.all(). Em seguida, verificamos se o usuário logado é um superusuário (staff). Se for, retornamos a queryset completa, permitindo que ele veja todos os usuários. Caso contrário, filtramos a queryset para retornar apenas o usuário logado, usando qs.filter(user=self.request.user). Isso garante que um usuário comum só possa acessar seus próprios dados, enquanto um superusuário pode acessar os dados de todos os usuários.
 
        if self.request.user.is_staff:
            return qs
       
        return qs.filter(user=self.request.user)
   
    def get_serializer_class(self):
        if self.action == "me":
            return PerfilSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path="me",
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        usuario = Usuario.objects.filter(user=request.user).first()
        if not usuario:
            return Response({"detail":"Perfil de usuário não encontrado."}, status=404)

        if request.method == 'PATCH':
            serializer = self.get_serializer(usuario, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path="alterar-senha",
        permission_classes=[IsAuthenticated]
    )
    def alterar_senha(self, request):
        senha_atual = request.data.get('senha_atual')
        nova_senha = request.data.get('nova_senha')
        confirmar_senha = request.data.get('confirmar_senha')

        if not request.user.check_password(senha_atual or ''):
            return Response({"detail": "Senha atual incorreta."}, status=400)

        if not nova_senha or nova_senha != confirmar_senha:
            return Response({"detail": "As novas senhas não coincidem."}, status=400)

        try:
            validate_password(nova_senha, user=request.user)
        except DjangoValidationError as exc:
            return Response({"detail": list(exc.messages)}, status=400)

        request.user.set_password(nova_senha)
        request.user.save()

        return Response({"detail": "Senha alterada com sucesso."})

    @action(
        detail=False,
        methods=['get'],
        url_path="exportar-dados",
        permission_classes=[IsAuthenticated]
    )
    def exportar_dados(self, request):
        usuario = Usuario.objects.filter(user=request.user).first()
        if not usuario:
            return Response({"detail": "Perfil de usuário não encontrado."}, status=404)

        conversas = Conversa.objects.filter(usuario=usuario)

        dados = {
            "perfil": {
                "nome": usuario.nome,
                "email": usuario.email,
                "data_criacao": usuario.data_criacao,
            },
            "conversas": [
                {
                    "id": conversa.id,
                    "titulo": conversa.titulo,
                    "mensagens": [
                        {
                            "remetente": mensagem.remetente,
                            "texto": mensagem.texto,
                            "data_envio": mensagem.data_envio,
                        }
                        for mensagem in conversa.mensagem_set.all()
                    ],
                }
                for conversa in conversas
            ],
        }

        response = JsonResponse(dados)
        response["Content-Disposition"] = 'attachment; filename="meus_dados.json"'
        return response

    @action(
        detail=False,
        methods=['delete'],
        url_path="apagar-conversas",
        permission_classes=[IsAuthenticated]
    )
    def apagar_conversas(self, request):
        usuario = Usuario.objects.filter(user=request.user).first()
        if not usuario:
            return Response({"detail": "Perfil de usuário não encontrado."}, status=404)

        quantidade, _ = Conversa.objects.filter(usuario=usuario).delete()
        return Response({"detail": "Conversas apagadas com sucesso.", "quantidade": quantidade})

    @action(
        detail=False,
        methods=['delete'],
        url_path="excluir-conta",
        permission_classes=[IsAuthenticated]
    )
    def excluir_conta(self, request):
        senha = request.data.get('senha')

        if not senha or not request.user.check_password(senha):
            return Response({"detail": "Senha incorreta."}, status=400)

        request.user.delete()
        return Response({"detail": "Conta excluída com sucesso."})

    @action(
        detail=False,
        methods=['get'],
        url_path="tipo-choices",
        permission_classes=[AllowAny]
    )
    def tipo_choices(self, request):
        return Response([
            {"value": v, "label": l}
            for v, l in Usuario.TIPO_CHOICES
        ])
   
 
class RegisterView(APIView):

    permission_classes = [AllowAny] # permite que qualquer pessoa que ainda não tem o acesso entre na rota de registro, ou seja, não exige autenticação para acessar essa view. Isso é importante porque, se colocássemos IsAuthenticated aqui, ninguém conseguiria se registrar, já que o registro é a porta de entrada para obter acesso ao sistema. Portanto, AllowAny é a escolha correta para permitir que novos usuários criem suas contas sem precisar estar autenticados previamente.

    def post(self, request):

        serializer = RegisterSerializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Usuário criado com sucesso."},
            status=status.HTTP_201_CREATED
        )



class MensagemViewSet(ModelViewSet):
    queryset = Mensagem.objects.all()
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]
    
    # Diferente do modelo de IA, aqui o filtro é essencial para buscar 
    # as mensagens de uma conversa específica (ex: ?conversa=1)
    filter_backends = [DjangoFilterBackend]
    filterset_class = MensagemFilter

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Se for staff, tem visão total (auditoria)
        if self.request.user.is_staff:
            return qs
            
        # Filtra as mensagens através da relação com a conversa e o usuário
        # "conversa_usuario_user" segue o caminho: Mensagem -> Conversa -> Usuario -> User
        return qs.filter(conversa_usuario_user=self.request.user)

    def perform_create(self, serializer):
    
        # Aqui você pode garantir que o usuário não está tentando enviar uma mensagem
        # para uma conversa que não pertence a ele.
        conversa = serializer.validated_data.get('conversa')
        
        if not self.request.user.is_staff and conversa.usuario.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Você não tem permissão para enviar mensagens nesta conversa.")
            
        serializer.save()




class ConversaViewSet(ModelViewSet):

    queryset = Conversa.objects.all()
    serializer_class = ConversaSerializer
    permission_classes = [IsAuthenticated]
    
    # Adicionando suporte a filtros (ex: filtrar por data ou título)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversaFilter # Certifique-se de ter essa classe no seu filters.py

    def get_queryset(self):
    
        qs = super().get_queryset()
        
        # Se for administrador da empresa (staff), retorna todas as conversas
        if self.request.user.is_staff:
            return qs
        
        # Se for usuário comum, filtra para retornar apenas as conversas 
        # vinculadas ao perfil do usuário logado.
        # (Considerando que na sua model Conversa existe um campo FK chamado 'usuario')
        return qs.filter(usuario__user=self.request.user)

    def perform_create(self, serializer):

        # Busca o perfil do usuário logado
        usuario_perfil = Usuario.objects.filter(user=self.request.user).first()
        if not usuario_perfil:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Perfil de usuário não encontrado para o usuário autenticado.")

        serializer.save(usuario=usuario_perfil)





class ModeloIAViewSet(ModelViewSet):

    queryset = ModeloIA.objects.all() 
    serializer_class = ModeloIASerializer
    
    # Aqui permitimos que qualquer usuário autenticado veja os modelos,
    # mas você pode restringir a criação/edição apenas para o Admin no futuro.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
      
        return ModeloIA.objects.all()

    @action(detail=False, methods=['get'], url_path="ativos")
    def modelos_ativos(self, request):
        """
        Uma rota extra caso você queira retornar apenas os modelos 
        que a empresa liberou para uso no momento.
        """
        ativos = self.queryset.filter(ativo=True) # Supondo que exista um campo 'ativo'
        serializer = self.get_serializer(ativos, many=True)
        return Response(serializer.data)
    

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(
            username=email,
            password=password
        )

        if user is not None:

            refresh = RefreshToken.for_user(user)

            usuario = Usuario.objects.filter(user=user).first()
            nome = usuario.nome if usuario else user.username

            return Response({
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "nome": nome,
                "message": "Login realizado com sucesso"
            })

        return Response({
            "success": False,
            "message": "Email ou senha inválidos"
        }, status=400)

@login_required
def google_login_redirect(request):
    """
    Chamada pelo django-allauth logo após o Google confirmar o login
    (autenticação por sessão). Aqui geramos o JWT do usuário e mandamos
    ele de volta pro front já com os dados na URL, do mesmo jeito que
    o LoginView normal devolve no corpo da resposta.
    """
    try:
        user = request.user

        usuario, _ = Usuario.objects.get_or_create(
            user=user,
            defaults={
                'nome': f"{user.first_name} {user.last_name}".strip() or user.email,
                'email': user.email,
                'senha': '',
            }
        )

        refresh = RefreshToken.for_user(user)

        params = urlencode({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "nome": usuario.nome,
        })

        return redirect(f"http://localhost:5173/chat?{params}")
    except Exception:
        import logging
        logging.getLogger("Api").exception("Falha ao concluir login via Google")
        return redirect("http://localhost:5173/login?erro=google_login_falhou")


def confirmar_email(request, key):
    """
    Substitui a tela padrão (e feia) do allauth para confirmação de e-mail.
    Confirma o e-mail nos bastidores e redireciona direto para o React,
    que decide o que mostrar com base no parâmetro `email_confirmado`.
    """
    confirmation = EmailConfirmationHMAC.from_key(key)

    if confirmation:
        confirmation.confirm(request)
        return redirect(f"{FRONTEND_URL}/login?email_confirmado=1")

    # Se a key não bate mais com um EmailAddress "verified=False", pode ser
    # porque já foi confirmada antes (link clicado de novo) ou porque expirou/é inválida.
    try:
        max_age = 60 * 60 * 24 * allauth_account_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
        pk = signing.loads(key, max_age=max_age, salt=allauth_account_settings.SALT)
        email_address = EmailAddress.objects.filter(pk=pk).first()
    except signing.SignatureExpired:
        return redirect(f"{FRONTEND_URL}/login?email_confirmado=expirado")
    except signing.BadSignature:
        email_address = None

    if email_address and email_address.verified:
        return redirect(f"{FRONTEND_URL}/login?email_confirmado=ja_confirmado")

    return redirect(f"{FRONTEND_URL}/login?email_confirmado=invalido")


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Exige o Token JWT enviado pelo React
def obter_usuario_atual(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "nome": getattr(request.user, 'nome', request.user.first_name) # Pega o nome salvo
    })