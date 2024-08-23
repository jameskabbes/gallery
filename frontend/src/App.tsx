import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Studios } from './components/Studio/pages/Studios';
import { Studio } from './components/Studio/pages/Studio';
import { ApplicationContextProvider } from './contexts/Application';
import { Toast } from './components/Toast';
import { Modals } from './components/Modals';
import { Profile } from './components/User/pages/Profile';
import { Login } from './components/Login';
import { SignUp } from './components/SignUp';

function App(): JSX.Element {
  return (
    <ApplicationContextProvider>
      <div className="App">
        <Login />
        {/* <SignUp /> */}
        <Modals />
        <Toast />
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
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
