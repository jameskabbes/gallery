import React, { useEffect, useRef, useContext } from 'react';
import { CSSTransition } from 'react-transition-group';
import { ModalsContext } from '../contexts/Modals';
import './Modal.css';

function Modals() {
  const modalsContext = useContext(ModalsContext);
  const currentModal =
    modalsContext.state.stack[modalsContext.state.stack.length - 1];
  const nodeRef = useRef(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        modalsContext.dispatch({ type: 'POP' });
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <CSSTransition
      nodeRef={nodeRef}
      in={currentModal !== undefined}
      timeout={200}
      classNames="modal"
      unmountOnExit
    >
      <div
        ref={nodeRef}
        className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center"
      >
        {currentModal}
      </div>
    </CSSTransition>
  );
}

export { Modals };
