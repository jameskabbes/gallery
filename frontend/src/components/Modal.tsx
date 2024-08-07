import React, { useEffect, useRef } from 'react';
import { CSSTransition } from 'react-transition-group';
import './Modal.css'; // Import the CSS file for animations

interface Props {
  children: React.ReactNode;
  close: () => void;
}

function Modal({ children, close }: Props) {
  const nodeRef = useRef(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        close();
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
      timeout={300}
      classNames="modal"
      mountOnEnter
      unmountOnExit
    >
      <div className="modal">{children}</div>
    </CSSTransition>
  );
}

export { Modal };
