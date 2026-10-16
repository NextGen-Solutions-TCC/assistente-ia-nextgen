from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, TransactionTestCase, override_settings
from unittest.mock import Mock, patch

from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from .models import Conversa, Mensagem, Usuario


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario-legado',
            email='pessoa@example.com',
            password='Teste-seguro-2026!',
        )

    def test_login_accepts_email_when_username_is_different(self):
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True,
        )

        response = self.client.post(
            '/Api/login/',
            {'email': ' PESSOA@EXAMPLE.COM ', 'password': 'Teste-seguro-2026!'},
            HTTP_HOST='127.0.0.1',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_login_still_requires_email_confirmation(self):
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=False,
        )

        response = self.client.post(
            '/Api/login/',
            {'email': self.user.email, 'password': 'Teste-seguro-2026!'},
            HTTP_HOST='127.0.0.1',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('Confirme seu e-mail', response.json()['message'])


class ConversationHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='historico-user',
            email='historico@example.com',
            password='Teste-seguro-2026!',
        )
        self.profile = Usuario.objects.create(
            user=self.user,
            nome='Pessoa do Histórico',
            email=self.user.email,
            senha='',
        )
        self.conversation = Conversa.objects.create(
            usuario=self.profile,
            titulo='Conversa de teste',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_sending_message_creates_conversation_and_saves_message(self):
        response = self.client.post(
            '/Api/conversa/enviar/',
            {'texto': 'Como posso começar?'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        conversa = Conversa.objects.get(pk=response.json()['conversa']['id'])
        mensagem = Mensagem.objects.get(conversa=conversa)
        self.assertEqual(conversa.usuario, self.profile)
        self.assertEqual(conversa.titulo, 'Como posso começar?')
        self.assertEqual(mensagem.remetente, 'user')
        self.assertEqual(mensagem.texto, 'Como posso começar?')

        conversation_response = self.client.get('/Api/conversa/')
        message_response = self.client.get(
            '/Api/mensagem/',
            {'conversa': conversa.id},
        )
        self.assertEqual(conversation_response.status_code, 200)
        self.assertEqual(
            {item['id'] for item in conversation_response.json()},
            {self.conversation.id, conversa.id},
        )
        self.assertEqual(message_response.status_code, 200)
        self.assertEqual(
            [item['texto'] for item in message_response.json()],
            ['Como posso começar?'],
        )

    def test_sending_message_to_another_users_conversation_is_rejected(self):
        another_user = User.objects.create_user(
            username='outro-user',
            email='outro@example.com',
            password='Teste-seguro-2026!',
        )
        another_profile = Usuario.objects.create(
            user=another_user,
            nome='Outra Pessoa',
            email=another_user.email,
            senha='',
        )
        conversa = Conversa.objects.create(
            usuario=another_profile,
            titulo='Conversa privada',
        )

        response = self.client.post(
            '/Api/conversa/enviar/',
            {'conversa': conversa.id, 'texto': 'Mensagem indevida'},
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Mensagem.objects.filter(conversa=conversa).exists())

    @override_settings(
        LANGFLOW_BASE_URL='http://langflow.test',
        LANGFLOW_FLOW_ID='test-flow',
        LANGFLOW_API_KEY='test-api-key',
    )
    @patch('Api.views.requests.post')
    def test_chatbot_saves_langflow_reply_to_conversation(self, post):
        user_message = Mensagem.objects.create(
            conversa=self.conversation,
            remetente='user',
            texto='Como posso começar?',
        )
        response_from_langflow = Mock()
        response_from_langflow.json.return_value = {
            'outputs': [{
                'outputs': [{
                    'results': {
                        'message': {'text': 'Comece pelo painel principal.'}
                    }
                }]
            }]
        }
        post.return_value = response_from_langflow

        response = self.client.post(
            '/Api/chatbot/',
            {
                'conversation_id': self.conversation.id,
                'message': user_message.texto,
                'context': 'geral',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        response_from_langflow.raise_for_status.assert_called_once()
        post.assert_called_once()
        self.assertEqual(
            post.call_args.args[0],
            'http://langflow.test/api/v1/run/test-flow',
        )
        self.assertEqual(
            post.call_args.kwargs['headers']['x-api-key'],
            'test-api-key',
        )
        payload = post.call_args.kwargs['json']
        self.assertIn('Contexto do produto: Geral', payload['input_value'])
        self.assertEqual(
            payload['session_id'],
            f'user-{self.user.pk}-conversation-{self.conversation.pk}',
        )
        self.assertEqual(response.json()['message'], 'Comece pelo painel principal.')
        self.assertTrue(
            Mensagem.objects.filter(
                conversa=self.conversation,
                remetente='bot',
                texto='Comece pelo painel principal.',
            ).exists()
        )

    def test_chatbot_returns_service_unavailable_when_not_configured(self):
        conversation = Conversa.objects.create(
            usuario=self.profile,
            titulo='Pergunta inicial',
        )
        Mensagem.objects.create(
            conversa=conversation,
            remetente='user',
            texto='Pergunta inicial',
        )

        with override_settings(LANGFLOW_BASE_URL='', LANGFLOW_FLOW_ID=''):
            response = self.client.post(
                '/Api/chatbot/',
                {
                    'conversation_id': conversation.id,
                    'message': 'Pergunta inicial',
                    'context': 'geral',
                },
                format='json',
            )

        self.assertEqual(response.status_code, 503)
        self.assertFalse(
            Mensagem.objects.filter(conversa=conversation, remetente='bot').exists()
        )


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class RegistrationConfirmationTests(TransactionTestCase):
    def test_registration_sends_confirmation_email(self):
        response = self.client.post(
            '/Api/auth/register/',
            {
                'username': 'nova.pessoa@example.com',
                'email': 'Nova.Pessoa@example.com',
                'password': 'M4deira!Forte-2026',
                'confirmar_password': 'M4deira!Forte-2026',
                'nome': 'Nova Pessoa',
            },
            HTTP_HOST='127.0.0.1',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            'nova.pessoa@example.com',
            mail.outbox[0].to,
        )
