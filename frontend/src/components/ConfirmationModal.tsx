import React, { useContext, useRef } from 'react';
import { ConfirmationModalContext } from '../contexts/ConfirmationModal';

import { Modal } from './Modal';

function ConfirmationModal(): JSX.Element {
  let context = useContext(ConfirmationModalContext);

  return (
    <Modal close={() => context.dispatch({ type: 'CANCEL' })}>
      <div className="modal flex justify-center items-center">
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
    </Modal>
  );
}

export { ConfirmationModal };
