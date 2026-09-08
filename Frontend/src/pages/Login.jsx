import "./Login.css";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";


import robot from "../assets/robot.svg";
import google from "../assets/google.png";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

const MENSAGENS_CONFIRMACAO_EMAIL = {
  "1": { tipo: "sucesso", texto: "E-mail confirmado com sucesso! Já pode entrar." },
  ja_confirmado: { tipo: "sucesso", texto: "Esse e-mail já tinha sido confirmado. Pode entrar normalmente." },
  expirado: { tipo: "erro", texto: "Esse link de confirmação expirou. Cadastre-se novamente ou peça um novo e-mail." },
  invalido: { tipo: "erro", texto: "Esse link de confirmação é inválido." },
};

const MENSAGENS_CADASTRO = {
  sucesso: {
    tipo: "sucesso",
    texto: "Cadastro realizado! Enviamos um e-mail de confirmação para o seu Gmail — verifique a caixa de entrada (e o spam) antes de entrar.",
  },
};

function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [errorEmail, setErrorEmail] = useState("");
  const [errorPassword, setErrorPassword] = useState("");
  const [errorGeral, setErrorGeral] = useState("");

  const avisoConfirmacao =
    MENSAGENS_CONFIRMACAO_EMAIL[searchParams.get("email_confirmado")] ||
    MENSAGENS_CADASTRO[searchParams.get("cadastro")];

  const validarEmail = (emailStr) => {
    return /\S+@\S+\.\S+/.test(emailStr);
  };

  const handleLogin = async () => {
    setErrorEmail("");
    setErrorPassword("");
    setErrorGeral("");

    let erroDetectado = false;

    if (!email && !password) {
      setErrorGeral("Preencha todos os campos");
      return;
    }

    if (!email) {
      setErrorEmail("O campo de e-mail é obrigatório");
      erroDetectado = true;
    } else if (!validarEmail(email)) {
      setErrorEmail("Digite um email válido");
      erroDetectado = true;
    }

    if (!password) {
      setErrorPassword("O campo de senha é obrigatório");
      erroDetectado = true;
    }

    if (erroDetectado) return;

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/Api/login/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        console.log("Sucesso:", data);

        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("user_name", data.nome);

        navigate("/chat");
      } else {
        setErrorGeral(data.message || "Email ou senha incorretos");
      }
    } catch (error) {
      console.error("Erro na conexão:", error);
      setErrorGeral("Não foi possível conectar ao servidor.");
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/accounts/google/login/?process=login";
  };

  return (
    <div className="container">
      <Card>
        <img src={robot} alt="robot" className="icon" />
        <h2>Bem vindo ao <span>LOGIN</span></h2>

        {avisoConfirmacao && (
          <span className={`error-message-inline geral ${avisoConfirmacao.tipo === "sucesso" ? "sucesso" : ""}`}>
            {avisoConfirmacao.texto}
          </span>
        )}

        {errorGeral && <span className="error-message-inline geral">{errorGeral}</span>}

        {/* CAMPO DE E-MAIL COM LABEL E PLACEHOLDER DE EXEMPLO */}
        <div className="input-group-validation">
          <div className="label-row">
            <label className="input-label">E-mail</label>
            {errorEmail && <span className="error-message-inline">{errorEmail}</span>}
          </div>
          <div className={errorEmail ? "input-error-wrapper" : ""}>
            <Input
              type="email"
              placeholder="Digite seu e-mail (Ex: nome@email.com)"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errorEmail) setErrorEmail("");
              }}
            />
          </div>
        </div>

        {/* CAMPO DE SENHA COM LABEL E PLACEHOLDER DE EXEMPLO */}
        <div className="input-group-validation">
          <div className="label-row">
            <label className="input-label">Senha</label>
            {errorPassword && <span className="error-message-inline">{errorPassword}</span>}
          </div>
          <div className={errorPassword ? "input-error-wrapper" : ""}>
            <Input
              type="password"
              placeholder="Digite sua senha (Mínimo 8 caracteres)"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errorPassword) setErrorPassword("");
              }}
            />
          </div>
        </div>

        <Link to="/esqueci-senha" style={{ textDecoration: "none", width: "100%" }}>
          <span className="forgot">esqueci minha senha</span>
        </Link>

        <Button text="Entrar" onClick={handleLogin} />

        <button className="google-btn" type="button" onClick={handleGoogleLogin}>
          <img src={google} alt="google" />
          Continuar com Google
        </button>

        <p className="signup">
          Não tem conta?
          <Link to="/cadastro">
            <span> Criar uma conta</span>
          </Link>
        </p>
      </Card>
    </div>
  );
}

export default Login;