import "./Cadastro.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import robot from "../assets/robot.svg";
import google from "../assets/google.png";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

function Cadastro() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeTerms, setAgreeTerms] = useState(false);

  // ESTADOS DE ERRO PARA EXIBIÇÃO NO CARD
  const [errorName, setErrorName] = useState("");
  const [errorEmail, setErrorEmail] = useState("");
  const [errorPassword, setErrorPassword] = useState("");
  const [errorConfirmPassword, setErrorConfirmPassword] = useState("");
  const [errorTerms, setErrorTerms] = useState("");
  const [errorGeral, setErrorGeral] = useState("");

  const validarEmail = (emailStr) => {
    return /\S+@\S+\.\S+/.test(emailStr);
  };

  const handleCadastro = async () => {
    // Resetar todos os erros a cada nova tentativa de submissão
    setErrorName("");
    setErrorEmail("");
    setErrorPassword("");
    setErrorConfirmPassword("");
    setErrorTerms("");
    setErrorGeral("");

    let erroDetectado = false;

    // 1. Validação Geral de Campos Vazios
    if (!name && !email && !password && !confirmPassword) {
      setErrorGeral("Preencha todos os campos para continuar");
      return;
    }

    if (!name) {
      setErrorName("O nome de usuário é obrigatório");
      erroDetectado = true;
    }

    if (!email) {
      setErrorEmail("O campo de e-mail é obrigatório");
      erroDetectado = true;
    } else if (!validarEmail(email)) {
      setErrorEmail("Digite um e-mail válido");
      erroDetectado = true;
    }

    if (!password) {
      setErrorPassword("A senha é obrigatória");
      erroDetectado = true;
    } else if (password.length < 8) {
      setErrorPassword("A senha deve ter no mínimo 8 caracteres");
      erroDetectado = true;
    }

    if (password !== confirmPassword) {
      setErrorConfirmPassword("As senhas não conferem");
      erroDetectado = true;
    }

    if (!agreeTerms) {
      setErrorTerms("Você precisa aceitar os termos para continuar");
      erroDetectado = true;
    }

    if (erroDetectado) return;

    try {
      // Como o seu LoginView usa o email no lugar do username,
      // enviamos o e-mail no campo username para manter consistência total no Django.
      const response = await fetch(
        "http://127.0.0.1:8000/Api/auth/register/", //local host:8000/Api/auth/register/ é 
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: email, // O serializer exige o username e sua login view busca por ele!
            email: email,            
            password: password,      
            nome: name,
            confirmar_password: confirmPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        // Redireciona para o login avisando para verificar o e-mail de confirmação
        navigate("/login?cadastro=sucesso");
      } else {
        // Mapeia erros vindos diretamente do banco de dados (Django Rest Framework)
        if (data.username) setErrorName("Nome de usuário inválido ou já existente.");
        if (data.email) setErrorEmail("Este e-mail já está cadastrado.");
        
        if (data.password) {
          setErrorPassword(Array.isArray(data.password) ? data.password[0] : data.password);
        } else if (data.non_field_errors) {
          setErrorGeral(data.non_field_errors[0]);
        } else {
          setErrorGeral("Erro ao realizar o cadastro. Verifique os dados ou mude o e-mail.");
        }
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
        <div className="robot-circle-blue">
          <img src={robot} alt="robot" className="icon-blue" />
        </div>
        
        <h2>Bem vindo ao <span>CADASTRO</span></h2>

        {/* MENSAGEM DE ERRO GLOBAL */}
        {errorGeral && <span className="error-message-inline geral">{errorGeral}</span>}

        {/* CAMPO: NOME */}
        <div className="input-group-validation">
          <div className="label-row">
            <label className="input-label">Nome Completo</label>
            {errorName && <span className="error-message-inline">{errorName}</span>}
          </div>
          <div className={errorName ? "input-error-wrapper" : ""}>
            <Input
              type="text"
              placeholder="Escreva seu nome completo"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (errorName) setErrorName("");
              }}
            />
          </div>
        </div>

        {/* CAMPO: EMAIL */}
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

        {/* CAMPO: SENHA */}
        <div className="input-group-validation">
          <div className="label-row">
            <label className="input-label">Senha</label>
            {errorPassword && <span className="error-message-inline">{errorPassword}</span>}
          </div>
          <div className={errorPassword ? "input-error-wrapper" : ""}>
            <Input
              type="password"
              placeholder="Crie uma senha forte (Mínimo 8 caracteres)"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errorPassword) setErrorPassword("");
              }}
            />
          </div>
        </div>

        {/* CAMPO: CONFIRMAR SENHA */}
        <div className="input-group-validation">
          <div className="label-row">
            <label className="input-label">Confirmar senha</label>
            {errorConfirmPassword && <span className="error-message-inline">{errorConfirmPassword}</span>}
          </div>
          <div className={errorConfirmPassword ? "input-error-wrapper" : ""}>
            <Input
              type="password"
              placeholder="Digite a senha novamente"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (errorConfirmPassword) setErrorConfirmPassword("");
              }}
            />
          </div>
        </div>

        {/* CHECKBOX TERMOS E CONDIÇÕES + ERRO INLINE INFERIOR */}
        <div className="checkbox-container-group">
          <div className="checkbox-area">
            <input
              type="checkbox"
              id="terms"
              checked={agreeTerms}
              onChange={(e) => {
                setAgreeTerms(e.target.checked);
                if (errorTerms) setErrorTerms("");
              }}
            />
            <label htmlFor="terms">Eu concordo com Termos e Condições</label>
          </div>
          {errorTerms && <span className="error-message-inline terms-error">{errorTerms}</span>}
        </div>

        <Button text="Cadastrar-se" onClick={handleCadastro} />

        <button className="google-btn" type="button" onClick={handleGoogleLogin}>
          <img src={google} alt="google" />
          Continuar com Google
        </button>

        <p className="login-text">
          Já tem conta? 
          <Link to="/login">
            <span> Entrar</span>
          </Link>
        </p>
      </Card>
    </div>
  );
}

export default Cadastro;