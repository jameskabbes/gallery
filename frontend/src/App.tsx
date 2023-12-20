import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';

function App(): JSX.Element {
  return (
    <div className="App">
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/404" element={<p>404</p>} />
          <Route path="*" element={<Navigate to="/404" />} />
        </Routes>
        <Footer />
      </BrowserRouter>
    </div>
  );
}

export { App };
