# Erros arrumados

Registro dos erros/problemas encontrados no projeto e como foram corrigidos.

## 1. Não existia usuário admin

**Problema:** Não havia nenhum superusuário criado para acessar o Django Admin.

**Correção:** Criado um novo superusuário:
- Usuário: `Gajura`
- Senha: `123`

## 2. Login com Google não funcionava

**Problema:** O login social via Google (django-allauth / dj-rest-auth) não estava autenticando.

**Correção:**
- No Google Cloud Console, projeto **GenIA**, foram obtidas as credenciais OAuth (Client ID e Client Secret).
- Essas credenciais foram cadastradas em **Social Applications**, dentro da tela do Django Admin.
- Em **Sites**, foi adicionada a rota `http://127.0.0.1:8000/` e associada à Social Application do Google.
- Foi identificado que em `settings.py` a variável `SITE_ID` estava configurada como `1`, mas o Site criado/usado no admin correspondia ao `id 2`. Corrigido `SITE_ID` para `2` em `Backend/GenAI/settings.py`, o que resolveu o login com Google.

## 3. Django rejeitava requisições locais

**Problema:** `ALLOWED_HOSTS` estava vazio. O Django rejeitava requisições feitas para `localhost` e `127.0.0.1` antes de elas chegarem às views, inclusive as de login.

**Correção:** `Backend/GenAI/settings.py` passou a permitir esses hosts por padrão e a ler hosts adicionais da variável `DJANGO_ALLOWED_HOSTS`. A variável também foi documentada em `Backend/.env.example`.

**Validação:** os dois testes específicos de login passaram depois da alteração.

## 4. Configuração de e-mail pelo Gmail

**Problema:** sem credenciais SMTP, o Django usava o backend de console e apenas imprimia os e-mails no terminal.

**Correção:** `Backend/GenAI/settings.py` usa o SMTP do Gmail e lê `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` de `Backend/.env`. Se as credenciais não estiverem configuradas em desenvolvimento, o backend de console continua sendo usado. As variáveis foram documentadas em `Backend/.env.example`.

**Observação:** o `.env` local é ignorado pelo Git; cada pessoa que clonar o projeto deve criar seu próprio arquivo com as credenciais. Nenhuma senha foi adicionada ao código ou a este documento. A configuração foi carregada e conferida localmente, mas não foi feito envio real de e-mail de teste.

## 5. Mensagens não eram persistidas no histórico

**Problema:** as mensagens do chat ficavam apenas no estado do frontend; o backend não oferecia uma operação específica para criar uma conversa e salvar a mensagem do usuário no mesmo fluxo.

**Correção no backend:**
- Adicionada a ação autenticada `POST /Api/conversa/enviar/`.
- Ao iniciar conversa, o backend cria a conversa associada ao perfil do usuário e usa a primeira mensagem como título.
- Ao continuar conversa, verifica se ela pertence ao usuário autenticado antes de salvar a mensagem.
- As conversas e mensagens são listadas em ordem para permitir carregar o histórico.
- Corrigido o filtro da API de mensagens para usar o relacionamento válido `conversa__usuario__user`.
- Ajustado o serializer de conversa para tratar `usuario` como somente leitura; o perfil é definido pelo backend.

Não foi necessário criar migração: foram usados os modelos `Conversa` e `Mensagem` já existentes.

## 6. Integração do chatbot com Langflow

**Problema:** o frontend chamava `/Api/chatbot/`, mas a rota não estava implementada no backend.

**Correção no backend:**
- Criada a rota autenticada `POST /Api/chatbot/`.
- A requisição recebe `conversation_id`, `message` e `context` (`geral`, `condominios` ou `imobiliarias`).
- O backend confirma que a conversa pertence ao usuário, chama o endpoint `/api/v1/run/{LANGFLOW_FLOW_ID}` do Langflow e envia um `session_id` estável para manter a sessão por usuário e conversa.
- Quando há uma resposta textual válida, ela é gravada como mensagem do bot na conversa e devolvida ao chamador.
- Erros e indisponibilidade do Langflow retornam respostas HTTP apropriadas. A mensagem do usuário já salva permanece no histórico.
- URL base, ID do flow e chave opcional são lidos de `LANGFLOW_BASE_URL`, `LANGFLOW_FLOW_ID` e `LANGFLOW_API_KEY` em `Backend/.env`; os nomes foram adicionados a `Backend/.env.example` e documentados no `README.md`.

**Configuração pendente:** é necessário informar o endereço do Langflow e o ID do flow no `.env`. Uma chave só é necessária se a instância exigir autenticação. A integração foi validada com resposta simulada nos testes; não foi chamada uma instância Langflow real.

## 7. Alterações de frontend do histórico foram revertidas

Foi implementada uma interface para listar e reabrir conversas, mas, a pedido, todas as alterações feitas nesta tarefa em `Frontend/src/pages/Chatgeral.jsx` e `Frontend/src/pages/Chatgeral.css` foram desfeitas. Os arquivos voltaram ao estado anterior; portanto, o frontend atual ainda precisa chamar as rotas do backend para persistir mensagens, mostrar as respostas do chatbot e exibir/reabrir o histórico.

### Contrato esperado para o frontend

1. Enviar o JWT no cabeçalho `Authorization: Bearer <token>`.
2. Para salvar a mensagem do usuário, chamar `POST /Api/conversa/enviar/` com `{"texto": "mensagem", "conversa": null}` para uma nova conversa ou com o ID existente em `conversa` para continuar.
3. Usar o `conversa.id` retornado e chamar `POST /Api/chatbot/` com `{"conversation_id": id, "message": "mensagem", "context": "geral"}`. O contexto pode ser `geral`, `condominios` ou `imobiliarias`.
4. Exibir o campo `message` retornado. Não salvar a resposta do bot novamente pelo frontend: o backend já a persiste.
5. Listar conversas com `GET /Api/conversa/` e carregar as mensagens de uma conversa com `GET /Api/mensagem/?conversa=<id>`.

### Validação

- `python manage.py test Api.tests --verbosity 1`: 7 testes passaram, incluindo persistência, acesso à conversa de outro usuário, chamada simulada ao Langflow e ausência de configuração.
- `python manage.py check`: executou sem erros bloqueantes; reportou avisos existentes sobre chaves primárias padrão e restrições condicionais no MySQL.
- `npm run build`: passou antes da reversão das alterações do frontend.
- O lint completo do frontend já reportava problemas em arquivos existentes; não foi corrigido como parte do trabalho de backend.
