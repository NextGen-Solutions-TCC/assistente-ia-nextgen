from django.contrib.auth.models import User
from django.db import models

class Usuario(models.Model):
    TIPO_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='user')
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=123)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class ModeloIA(models.Model):
    nome_modelo = models.CharField(max_length=100)
    versao = models.CharField(max_length=50)
    data_lancamento = models.DateField()

    def __str__(self):
        return f"{self.nome_modelo} - {self.versao}"

class Conversa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.TextField(blank=True)

    def __str__(self):
        return f"Chat {self.id}: {self.titulo[:30]}"

class Mensagem(models.Model):
    # Relacionamentos
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE)
    modelo = models.ForeignKey(ModeloIA, on_delete=models.SET_NULL, null=True)
    
    remetente = models.CharField(max_length=50) 
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.remetente}: {self.texto[:20]}..."
    
    
# Create your models here.