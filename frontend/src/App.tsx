import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { ApplicationContextProvider } from './contexts/Application';
import { Toast } from './components/Toast/Toast';
import { Gallery } from './pages/Gallery';
import { Settings } from './pages/Settings';
import { Modals } from './components/Modal/Modals';
import { Surface } from './components/Utils/Surface';
import { VerifySignUp } from './components/Auth/SignUp';
import { Styles } from './pages/Styles';
// import { LogInWithMagicLink } from './components/Auth/MagicLink';
import { config } from './config/config';

import { VerifyMagicLink } from './components/Auth/MagicLink';

export function App(): JSX.Element {
  return (
    <ApplicationContextProvider>
      <Surface>
        <main id="app">
          <Toast />
          <Modals />
          <BrowserRouter>
            <Header />
            <Routes>
              <Route path="/" element={<Home />} />
              {/* /galleries */}
              <Route
                path={`${config.frontendRoutes.galleries}`}
                element={<Gallery root={true} />}
              />
              {/* /galleries/galleryId */}
              <Route
                path={`${config.frontendRoutes.galleries}/:galleryId`}
                element={<Gallery root={false} />}
              />
              <Route
                path={`${config.frontendRoutes.verify_signup}`}
                element={<VerifySignUp />}
              />
              <Route
                path={`${config.frontendRoutes.verify_magic_link}`}
                element={<VerifyMagicLink />}
              />

              <Route path="/settings/:selection" element={<Settings />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/styles" element={<Styles />} />
              <Route path="/settings/" element={<Settings />} />
              <Route path="/404" element={<p>404</p>} />
              <Route path="*" element={<Navigate to="/404" />} />
              {/* <Route
                path={`${config.frontend_urls.magic_link}`}
                element={<LogInWithMagicLink />}
              /> */}
            </Routes>
            <Footer />
          </BrowserRouter>
        </main>
      </Surface>
    </ApplicationContextProvider>
  );
}
