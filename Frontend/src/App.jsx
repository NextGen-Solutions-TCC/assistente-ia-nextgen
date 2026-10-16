import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Welcome from './pages/Welcome';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import ChatGeral from './pages/ChatGeral';
import Error500 from './pages/Error500';
import Error404 from './pages/Error404'; // Importe a nova tela

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/esqueci-senha" element={<ForgotPassword />} />
        <Route path="/redefinir-senha/:uid/:token" element={<ResetPassword />} />
        <Route path="/chat" element={<ChatGeral />} />

        {/* Telas de Erro */}
        <Route path="/erro-servidor" element={<Error500 />} />
        <Route path="/nao-encontrado" element={<Error404 />} />

        {/* Captura qualquer rota inexistente no navegador e exibe o 404 */}
        <Route path="*" element={<Error404 />} />
      </Routes>
    </Router>
  );
}

export default App;