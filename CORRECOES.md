# Correções — Autenticação e confirmação de e-mail

Resumo do que foi arrumado no fluxo de cadastro/login com JWT manual + verificação de e-mail via Gmail.

## 1. E-mail de confirmação não era enviado

**Arquivo:** `Backend/Api/serializers.py` (`RegisterSerializer.create`)

Antes, o código só criava o registro `EmailAddress` no banco (`EmailAddress.objects.create(...)`), o que não dispara nenhum envio — é só uma linha no banco. Passou a chamar `email_address.send_confirmation(request, signup=True)` dentro de `transaction.on_commit(...)`, que é o método do allauth que de fato gera o link e envia o e-mail. Só dispara se o cadastro (User + Usuario + EmailAddress) for concluído com sucesso.

**Arquivo:** `Backend/Api/views.py` (`RegisterView.post`)

Passou a enviar `context={'request': request}` para o serializer, necessário para o allauth montar a URL absoluta do link de confirmação.

**Arquivo:** `Backend/GenAI/settings.py`

- `EMAIL_BACKEND` trocado de `console` (só imprime no terminal) para `smtp` real (Gmail).
- `ACCOUNT_EMAIL_VERIFICATION` trocado de `'none'` para `'mandatory'`.

## 2. Tela de confirmação feia/estranha (padrão do allauth)

Ao clicar no link do e-mail, aparecia uma página HTML crua do Django/allauth ("Confirm Email Address"), sem nada a ver com o visual do app.

**Arquivo:** `Backend/Api/views.py` — nova view `confirmar_email(request, key)`:
- Confirma o e-mail nos bastidores.
- Redireciona direto para o React (`/login`) com um parâmetro `email_confirmado` indicando o resultado: `1` (sucesso), `ja_confirmado`, `expirado` ou `invalido`.

**Arquivo:** `Backend/GenAI/urls.py`

Rota `accounts/confirm-email/<key>/` sobrescrita **antes** do `include('allauth.urls')`, para usar a view customizada em vez da padrão.

**Arquivo:** `Frontend/src/pages/Login.jsx` + `Login.css`

Lê o parâmetro `email_confirmado` da URL e mostra a mensagem correspondente na própria tela de login (verde para sucesso, vermelho para erro), em vez do usuário ver uma página do Django.

## 3. Faltava avisar o usuário para checar o Gmail

Depois de se cadastrar, o usuário não sabia que precisava confirmar o e-mail antes de logar.

**Arquivo:** `Frontend/src/pages/Cadastro.jsx`

Ao concluir o cadastro com sucesso, redireciona para `/login?cadastro=sucesso` em vez de `/login` puro.

**Arquivo:** `Frontend/src/pages/Login.jsx`

Mostra a mensagem: *"Cadastro realizado! Enviamos um e-mail de confirmação para o seu Gmail — verifique a caixa de entrada (e o spam) antes de entrar."*

## 4. Apagar usuário deixava e-mail "preso" (órfão)

Ao apagar um usuário pela tela "Usuarios" do admin (ou pela API), só o registro `Usuario` era removido — o `User` do Django (com o mesmo e-mail) continuava no banco, bloqueando novos cadastros com aquele e-mail por "e-mail já cadastrado". Isso porque `Usuario.user` tem `on_delete=CASCADE` (apagar o `User` apaga o `Usuario`), mas o caminho inverso não existia.

**Arquivo:** `Backend/Api/signals.py`

Novo signal `post_delete` em `Usuario` que apaga o `User` correspondente junto, cobrindo qualquer forma de exclusão (admin, API, shell).

## Arquivos alterados

- `Backend/Api/serializers.py`
- `Backend/Api/views.py`
- `Backend/Api/signals.py`
- `Backend/GenAI/settings.py`
- `Backend/GenAI/urls.py`
- `Frontend/src/pages/Login.jsx`
- `Frontend/src/pages/Login.css`
- `Frontend/src/pages/Cadastro.jsx`
