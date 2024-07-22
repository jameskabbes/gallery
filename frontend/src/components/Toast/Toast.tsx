import React, { useContext } from 'react';
import { ToastContext } from '../../contexts/Toast';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import './ToastAnimations.css';

function Toast(): JSX.Element {
  let context = useContext(ToastContext);

  if (context.state.toasts.size > 0) {
    return (
      <div className="fixed bottom-0 right-0 p-4 space-y-4">
        <TransitionGroup>
          {Array.from(context.state.toasts.values()).map((toast) => (
            <CSSTransition
              key={toast.id}
              timeout={300} // Match the duration of your CSS transitions
              classNames="toast"
            >
              <div className="card">
                <p>{toast.message}</p>
                <button
                  onClick={() =>
                    context.dispatch({ type: 'DELETE', payload: toast.id })
                  }
                >
                  Close
                </button>
              </div>
            </CSSTransition>
          ))}
        </TransitionGroup>
      </div>
    );
  }

  return null;
}

export { Toast };
