import React, { useContext, useEffect } from 'react';
import { ModalContext } from '../contexts/Modal';

function Modal({
  children,
  onCancel,
}: {
  children: React.ReactNode;
  onCancel: () => void;
}) {
  let context = useContext(ModalContext);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        context.dispatch({ type: 'POP' });
        onCancel();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return <div className="modal">{children}</div>;
}

export { Modal };
