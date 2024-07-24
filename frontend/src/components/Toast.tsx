import React, { useContext } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { IoMdClose } from 'react-icons/io';

function Toast(): JSX.Element {
  return (
    <ToastContainer
      position="bottom-right"
      pauseOnFocusLoss={false}
      pauseOnHover={false}
      hideProgressBar={true}
      closeButton={<IoMdClose />}
      toastClassName={'toast-card'}
      bodyClassName={'toast-body'}
    />
  );
}

export { Toast };
