import React, { useContext } from 'react';
import { ToastContext } from '../contexts/Toast';

function Toast(): JSX.Element {
  let context = useContext(ToastContext);

  if (context.state.toasts.size > 0) {
    return (
      <div className="fixed bottom-0 right-0 p-4 space-y-4">
        {Array.from(context.state.toasts.values()).map((toast) => (
          <div key={toast.id} className="card">
            <p>{toast.message}</p>
            <button
              onClick={() =>
                context.dispatch({ type: 'DELETE', payload: toast.id })
              }
            >
              Close
            </button>
          </div>
        ))}
      </div>
    );
  }

  return null;
}

export { Toast };
