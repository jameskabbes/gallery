import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { ApplicationContextProvider } from './contexts/Application';
import { Toast } from './components/Toast/Toast';
import { Profile } from './components/User/Profile';
import { Settings } from './components/Settings/Settings';
import { AuthModals } from './components/Auth/AuthModals';
import { GlobalModals } from './components/GlobalModals';
import { Gallery } from './components/Gallery/pages/Gallery';
import { VerifyMagicLink } from './components/Auth/VerifyMagicLink';

import config from '../../config.json';

function App(): JSX.Element {
  return (
    <ApplicationContextProvider>
      <div className="App">
        <Toast />
        <AuthModals />
        <GlobalModals />
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/settings/:selection" element={<Settings />} />
            <Route path="/galleries/:gallery_id" element={<Gallery />} />
            <Route path="/404" element={<p>404</p>} />
            <Route path="*" element={<Navigate to="/404" />} />
            <Route
              path={`${config.magic_link_frontend_url}`}
              element={<VerifyMagicLink />}
            />
          </Routes>
          <Footer />
        </BrowserRouter>
      </div>
    </ApplicationContextProvider>
  );
}

export { App };
