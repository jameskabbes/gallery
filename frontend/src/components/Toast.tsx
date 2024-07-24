import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const toastTemplate = {
  isLoading: false,
  autoClose: 3000,
  closeOnClick: true,
};

function Toast(): JSX.Element {
  return (
    <ToastContainer
      position="bottom-right"
      pauseOnFocusLoss={false}
      pauseOnHover={false}
      hideProgressBar={true}
    />
  );
}

export { Toast, toastTemplate };
