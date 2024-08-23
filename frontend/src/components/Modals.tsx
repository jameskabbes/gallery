import React, { useEffect, useRef, useContext } from 'react';
import { CSSTransition } from 'react-transition-group';
import { ModalsContext } from '../contexts/Modals';
import { useEscapeKey } from '../utils/useEscapeKey';
import './Modal.css';
import { useClickOutside } from '../utils/useClickOutside';

function Modals() {
  const modalsContext = useContext(ModalsContext);
  const currentModal =
    modalsContext.state.stack[modalsContext.state.stack.length - 1];
  const nodeRef = useRef(null);

  useEscapeKey(() => {
    modalsContext.dispatch({ type: 'POP' });
  });

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
