import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import GameSetupForm from './pages/GameSetupForm';
import GameRoom from './pages/GameRoom';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<GameSetupForm />} />
      <Route path="/:codigo" element={<GameRoom />} />
    </Routes>
  </BrowserRouter>
);
