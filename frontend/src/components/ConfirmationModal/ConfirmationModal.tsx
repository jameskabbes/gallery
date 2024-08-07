import React, { useContext, useRef } from 'react';
import { ConfirmationModalContext } from '../../contexts/ConfirmationModal';
import { CSSTransition } from 'react-transition-group';
import './ConfirmationModal.css'; // Import the CSS file for animations

function ConfirmationModal(): JSX.Element {
  let context = useContext(ConfirmationModalContext);
  const nodeRef = useRef(null);

  return (
    <CSSTransition
      nodeRef={nodeRef}
      in={context.state.isActive}
      timeout={300}
      classNames="modal"
      mountOnEnter
      unmountOnExit
    >
      <div
        ref={nodeRef}
        className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center"
      >
        <div className="p-4 card">
          <h4>{context.state.title}</h4>
          <p>{context.state.message}</p>
          <div className="flex flex-row justify-center space-x-2">
            <button onClick={() => context.dispatch({ type: 'CANCEL' })}>
              {context.state.cancelText}
            </button>
            <button onClick={() => context.dispatch({ type: 'CONFIRM' })}>
              {context.state.confirmText}
            </button>
          </div>
        </div>
      </div>
    </CSSTransition>
  );
}

export { ConfirmationModal };
