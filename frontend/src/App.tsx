import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Studios } from './pages/Studios';
import { Studio } from './pages/Studio';
import { CreateStudio } from './components/Studio/CreateStudio';
import { ApplicationContextProvider } from './contexts/Application';
import { ConfirmationModal } from './components/ConfirmationModal';
import { Toast } from './components/Toast';

function App(): JSX.Element {
  return (
    <ApplicationContextProvider>
      <div className="App">
        <ConfirmationModal />
        <Toast />
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/studios" element={<Studios />} />
            <Route path="/studios/:studioId" element={<Studio />} />
            <Route path="/404" element={<p>404</p>} />
            <Route path="*" element={<Navigate to="/404" />} />
          </Routes>
          <Footer />
        </BrowserRouter>
      </div>
    </ApplicationContextProvider>
  );
}

export { App };
