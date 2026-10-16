import "./ResetPassword.css";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import robot from "../assets/robot.svg";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

function ResetPassword() {
  const navigate = useNavigate();
  const { uid, token } = useParams();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [errorPassword, setErrorPassword] = useState("");
  const [errorConfirmPassword, setErrorConfirmPassword] = useState("");
  const [errorGeral, setErrorGeral] = useState("");
  const [isDone, setIsDone] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleResetPassword = async () => {
    setErrorPassword("");
    setErrorConfirmPassword("");
    setErrorGeral("");

    let erroDetectado = false;

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

    if (erroDetectado) return;

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/auth/password/reset/confirm/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            uid,
            token,
            new_password1: password,
            new_password2: confirmPassword,
          }),
        }
      );

      if (response.ok) {
        setIsDone(true);
      } else {
        const data = await response.json();
        setErrorGeral(
          data.new_password2?.[0] ||
          data.new_password1?.[0] ||
          data.token?.[0] ||
          data.uid?.[0] ||
          data.detail ||
          "Não foi possível redefinir a senha. O link pode ter expirado."
        );
      }
    } catch (error) {
      console.error("Erro na conexão:", error);
      setErrorGeral("Não foi possível conectar ao servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-container">
      <Card>
        <div className="robot-circle-blue">
          <img src={robot} alt="robot" className="icon-blue" />
        </div>

        {!isDone ? (
          <>
            <h2>Redefinir senha</h2>

            <p className="reset-description">
              Digite sua nova senha para concluir a redefinição.
            </p>

            {errorGeral && (
              <span className="error-message-inline geral">{errorGeral}</span>
            )}

            <div className="input-group-validation">
              {errorPassword && (
                <span className="error-message-inline">{errorPassword}</span>
              )}
              <div className={errorPassword ? "input-error-wrapper" : ""}>
                <Input
                  type="password"
                  placeholder="Nova senha (mínimo 8 caracteres)"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errorPassword) setErrorPassword("");
                  }}
                />
              </div>
            </div>

            <div className="input-group-validation">
              {errorConfirmPassword && (
                <span className="error-message-inline">{errorConfirmPassword}</span>
              )}
              <div className={errorConfirmPassword ? "input-error-wrapper" : ""}>
                <Input
                  type="password"
                  placeholder="Confirme a nova senha"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    if (errorConfirmPassword) setErrorConfirmPassword("");
                  }}
                />
              </div>
            </div>

            <Button
              text={loading ? "Enviando..." : "Redefinir senha"}
              onClick={handleResetPassword}
              disabled={loading}
            />
          </>
        ) : (
          <>
            <h2>Senha redefinida</h2>

            <p className="reset-description">
              Sua senha foi alterada com sucesso. Você já pode entrar com a
              nova senha.
            </p>

            <Button text="Ir para o login" onClick={() => navigate("/login")} />
          </>
        )}

        <p className="back-to-login">
          Voltar para{" "}
          <Link to="/login">
            <span>Login</span>
          </Link>
        </p>
      </Card>
    </div>
  );
}

export default ResetPassword;
