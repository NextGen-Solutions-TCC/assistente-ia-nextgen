# Assistente IA NextGen

Chatbot interno para suporte aos produtos da Superlógica. Monorepo com duas apps independentes: uma API REST em Python/Django (`Backend/`) e um SPA em React + Vite (`Frontend/`). A lógica de IA é orquestrada via **Langflow** — o Django apenas faz proxy das mensagens para o flow configurado lá.

## Estrutura do repositório

```
assistente-ia-/
├── Backend/
│   ├── GenAI/          # Config do projeto Django (settings, urls, wsgi/asgi)
│   ├── Api/            # Único app Django — toda a lógica de negócio
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── filters.py
│   │   ├── adapters.py
│   │   └── services.py
│   ├── Fluxos/         # Exports de flows do Langflow (.json)
│   └── requirements.txt
├── Frontend/
│   └── src/
│       ├── App.jsx     # Router principal
│       ├── pages/      # Telas (chat, login, cadastro...)
│       ├── components/
│       └── services/   # Camada Axios (Api.js)
└── docs/arquitetura/   # ADRs e avaliações técnicas
```

## Pré-requisitos

- Python 3.10+
- Node.js 18+
- Uma instância do **Langflow** rodando (local ou remota)

## Setup local

### Backend

```bash
cd Backend
python -m venv .venv 
.\.venv\Scripts\Activate
pip install -r requirements.txt   # ~580 pacotes — demora na primeira vez
python manage.py migrate
python manage.py runserver        # http://127.0.0.1:8000
```

### Crie um usuário para ser acessado na UI 
```bash
curl -X POST http://127.0.0.1:8000/Api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "teste2", "email": "teste2@teste.com", "password": "senha123", "tipo": "user"}'
```

> `requirements.txt` é grande (inclui LangChain, Anthropic SDK, vector DBs, OCR, áudio). Use um virtualenv dedicado.

### Frontend

```bash
cd Frontend
npm install
npm run dev    # http://localhost:5173
npm run build
npm run lint
```

## Variáveis de ambiente

Configure o envio de e-mails copiando `Backend/.env.example` para `Backend/.env` e substituindo os valores de exemplo. Use uma **senha de app do Google**, não a senha normal da conta; o Gmail exige a verificação em duas etapas para gerar uma.

| Variável | Onde usar | Observação |
|---|---|---|
| `EMAIL_HOST_USER` | `GenAI/settings.py` | Conta Gmail que enviará as confirmações |
| `EMAIL_HOST_PASSWORD` | `GenAI/settings.py` | Senha de app do Gmail |
| `SITE_ID` | `GenAI/settings.py` | ID do Site ligado à Social Application do Google (padrão: `1`) |
| `LANGFLOW_BASE_URL` | `GenAI/settings.py` | URL base do servidor Langflow, por exemplo `http://localhost:7860` |
| `LANGFLOW_FLOW_ID` | `GenAI/settings.py` | ID do flow que será executado |
| `LANGFLOW_API_KEY` | `GenAI/settings.py` | Chave da API Langflow, se a instância exigir autenticação |

Sem credenciais SMTP, o backend em desenvolvimento imprime o link de confirmação no terminal em vez de enviá-lo ao Gmail. Com credenciais configuradas, o link é enviado por SMTP. A confirmação continua obrigatória para login manual.

As credenciais OAuth do Google são cadastradas em **Social Applications** no Django Admin e precisam estar associadas ao Site cujo ID corresponde a `SITE_ID`. O callback OAuth local precisa estar autorizado no Google como `http://127.0.0.1:8000/accounts/google/login/callback/`.

Sem `LANGFLOW_BASE_URL` e `LANGFLOW_FLOW_ID`, `/Api/chatbot/` retorna `503` e não remove a mensagem já salva no histórico. Configure essas variáveis no `Backend/.env` e reinicie o Django quando o flow estiver pronto.

## API endpoints

Todos os endpoints ficam sob o prefixo `/Api/`.

| Endpoint | Método | Descrição |
|---|---|---|
| `/Api/token/` | POST | Obter par de tokens JWT |
| `/Api/token/refresh/` | POST | Renovar access token |
| `/Api/auth/register/` | POST | Cadastro de usuário |
| `/Api/login/` | POST | Login |
| `/Api/chatbot/` | POST | Enviar mensagem para o Langflow |
| `/Api/usuario/` | GET / POST | CRUD de usuários |
| `/Api/conversa/` | GET / POST | CRUD de conversas |
| `/Api/mensagem/` | GET / POST | CRUD de mensagens (filtrável por `conversa_id`) |
| `/Api/modeloAI/` | GET / POST | CRUD de modelos de IA |

**Auth:** JWT com access token de 60 min e refresh de 1 dia. O Frontend anexa o token automaticamente via interceptor Axios.

**Chatbot:** `POST /Api/chatbot/` requer JWT e recebe `conversation_id`, `message` e `context` (`geral`, `condominios` ou `imobiliarias`). O backend verifica a propriedade da conversa, envia o texto/contexto ao endpoint `/api/v1/run/{LANGFLOW_FLOW_ID}` do Langflow com um `session_id` estável por usuário e conversa, salva a resposta como mensagem do bot e retorna `message`, `conversation_id` e `message_id`.

## Rotas do Frontend

| Rota | Tela |
|---|---|
| `/` | Welcome |
| `/login` | Login |
| `/cadastro` | Cadastro |
| `/esqueci-senha` | Recuperação de senha |
| `/chat` | Chat principal (fallback) |

## Pontos críticos de integração

**Langflow é necessário para respostas da IA.** O endpoint `/Api/chatbot/` faz proxy HTTP para o Langflow. Se o serviço estiver fora, o backend devolve erro 502/504; a mensagem do usuário permanece salva no histórico. O identificador de sessão enviado ao flow permite que o componente de memória do Langflow mantenha o contexto da conversa.

**Google OAuth** exige uma Social Application do Google cadastrada no Django Admin e associada ao Site selecionado por `SITE_ID`.

**Banco de dados:** a configuração atual do backend usa MySQL. Para produção, reveja as credenciais e permissões configuradas em `GenAI/settings.py`.

## Modelos de dados

| Model | Campos principais |
|---|---|
| `Usuario` | Usuário customizado Django |
| `Conversa` | Agrupamento de mensagens por sessão |
| `Mensagem` | Texto de cada turno do chat, vinculado a `Conversa` |
| `ModeloIA` | Registro dos modelos de IA disponíveis |

## Documentação técnica

ADRs e avaliações de arquitetura ficam em [docs/arquitetura/](docs/arquitetura/).
