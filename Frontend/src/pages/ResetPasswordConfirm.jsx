import "./ForgotPassword.css";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import robot from "../assets/robot.svg";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

function ResetPasswordConfirm() {
  const navigate = useNavigate();
  const { uid, token } = useParams();

  const [password, setPassword] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");
  const [errorGeral, setErrorGeral] = useState("");
  const [mensagemSucesso, setMensagemSucesso] = useState("");

  const handleResetPassword = async () => {
    setErrorGeral("");
    setMensagemSucesso("");

    if (!password || !confirmarPassword) {
      setErrorGeral("Preencha os dois campos de senha.");
      return;
    }

    if (password !== confirmarPassword) {
      setErrorGeral("As senhas não coincidem.");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/auth/password/reset/confirm/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            uid,
            token,
            new_password1: password,
            new_password2: confirmarPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMensagemSucesso("Senha redefinida com sucesso! Redirecionando para o login...");
        setTimeout(() => navigate("/login"), 2000);
      } else {
        const primeiroErro =
          data.new_password2?.[0] ||
          data.new_password1?.[0] ||
          data.token?.[0] ||
          data.uid?.[0] ||
          "Não foi possível redefinir a senha. O link pode ter expirado.";
        setErrorGeral(primeiroErro);
      }
    } catch (error) {
      console.error("Erro na conexão:", error);
      setErrorGeral("Não foi possível conectar ao servidor.");
    }
  };

  return (
    <div className="forgot-container">
      <Card>
        <div className="robot-circle-blue">
          <img src={robot} alt="robot" className="icon-blue" />
        </div>

        <h2>Redefinir senha</h2>

        <p className="forgot-description">
          Digite sua nova senha abaixo.
        </p>

        <div className="input-group-validation">
          {errorGeral && <span className="error-message-inline">{errorGeral}</span>}
          {mensagemSucesso && <span className="success-message-inline">{mensagemSucesso}</span>}

          <Input
            type="password"
            placeholder="Nova senha"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (errorGeral) setErrorGeral("");
            }}
          />
        </div>

        <div className="input-group-validation">
          <Input
            type="password"
            placeholder="Confirmar nova senha"
            value={confirmarPassword}
            onChange={(e) => {
              setConfirmarPassword(e.target.value);
              if (errorGeral) setErrorGeral("");
            }}
          />
        </div>

        <Button text="Redefinir senha" onClick={handleResetPassword} />

        <p className="back-to-login">
          Voltar para <Link to="/login"><span>Login</span></Link>
        </p>
      </Card>
    </div>
  );
}

export default ResetPasswordConfirm;
