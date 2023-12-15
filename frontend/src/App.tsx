import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './Home';

function App(): JSX.Element {
  return (
    <div className="App">
      <BrowserRouter>
        <div className="mx-2">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/404" element={<p>404</p>} />
            <Route path="*" element={<Navigate to="/404" />} />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
}

export { App };
