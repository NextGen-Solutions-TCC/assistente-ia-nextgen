import django_filters
from .models import *
 
class UsuarioFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains') # lookup_expr='icontains' é usado para fazer uma busca que contenha o valor do campo, ou seja, o valor do campo deve conter o valor da busca. No caso do nome, queremos que a busca seja feita por nome, ou seja, o usuário pode digitar parte do nome e a busca vai retornar os usuários que contêm essa parte do nome.
    tipo = django_filters.CharFilter(field_name='tipo', lookup_expr='iexact') # lookup_expr='iexact' é usado para fazer uma busca exata, ou seja, o valor deve ser exatamente igual ao valor do campo. No caso do tipo, queremos que a busca seja exata, ou seja, o usuário deve escolher entre 'LOCADOR' ou 'LOCATARIO', e não queremos que ele possa digitar um valor diferente.
 
    class Meta:
        model = Usuario
        fields = ['nome', 'tipo']

class MensagemFilter(django_filters.FilterSet):
    texto = django_filters.CharFilter(field_name='texto', lookup_expr='icontains')
    conversa = django_filters.NumberFilter(field_name='conversa_id') # Essencial para carregar mensagens de um chat

    class Meta:
        model = Mensagem
        fields = ['texto', 'conversa']
 
class ConversaFilter(django_filters.FilterSet):
    titulo = django_filters.CharFilter(field_name='titulo', lookup_expr='icontains')
    data_criacao = django_filters.DateFilter(field_name='data_criacao', lookup_expr='gte') # SERVE para filtrar conversas criadas a partir de uma data específica

    class Meta:
        model = Conversa 
        fields = ['titulo']
 
class ModeloIAFilter(django_filters.FilterSet):
    # nome_modelo geralmente é texto, então usamos CharFilter (e não DateFilter)
    nome_modelo = django_filters.CharFilter(field_name='nome_modelo', lookup_expr='icontains')
    
    # Se versão for um número ou texto (ex: "1.0"), não use BooleanFilter (que é só True/False)
    versao = django_filters.CharFilter(field_name='versao', lookup_expr='iexact')
    
    # Se data_lançamento for uma data real, use DateFilter. Se for apenas o ano, NumberFilter está ok.
    data_lancamento = django_filters.DateFilter(field_name='data_lancamento', lookup_expr='gte')

    class Meta:
        model = ModeloIA # Corrigido de Pagamento para ModeloIA
        fields = ['nome_modelo', 'versao', 'data_lancamento']