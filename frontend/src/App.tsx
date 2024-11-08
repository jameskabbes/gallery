import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { ApplicationContextProvider } from './contexts/Application';
import { Toast } from './components/Toast/Toast';
import { Galleries } from './pages/Galleries';
import { Gallery } from './pages/Gallery';
import { Settings } from './pages/Settings';
import { AuthModals } from './components/Auth/AuthModals';
import { GlobalModals } from './components/GlobalModals';
import { VerifyMagicLink } from './components/Auth/VerifyMagicLink';
import { Surface } from './components/Utils/Surface';
import Styles from './pages/Styles';

import siteConfig from '../siteConfig.json';
import config from '../../config.json';

function App(): JSX.Element {
  return (
    <ApplicationContextProvider>
      <Surface>
        <main id="app">
          <Toast />
          <AuthModals />
          <GlobalModals />
          <BrowserRouter>
            <Header />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route
                path={`${siteConfig.galleriesUrlBase}`}
                element={<Galleries />}
              />
              <Route
                path={`${siteConfig.galleriesUrlBase}/:galleryId`}
                element={<Gallery />}
              />
              <Route path="/settings/:selection" element={<Settings />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/styles" element={<Styles />} />
              <Route path="/settings/" element={<Settings />} />
              <Route path="/404" element={<p>404</p>} />
              <Route path="*" element={<Navigate to="/404" />} />
              <Route
                path={`${config.magic_link_frontend_url}`}
                element={<VerifyMagicLink />}
              />
            </Routes>
            <Footer />
          </BrowserRouter>
        </main>
      </Surface>
    </ApplicationContextProvider>
  );
}

export { App };
