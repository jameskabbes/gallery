import React, { useContext, useRef } from 'react';
import { ModalContext } from '../contexts/Modal';
import { Modal } from './Modal';

interface Props {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
}

function ConfirmationModal({
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
}: Props): JSX.Element {
  let context = useContext(ModalContext);

  return (
    <Modal onCancel={onCancel}>
      <div className="p-4 card">
        <h4>{title}</h4>
        <p>{message}</p>
        <div className="flex flex-row justify-center space-x-2">
          <button
            onClick={() => {
              onCancel();
              context.dispatch({ type: 'POP' });
            }}
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              context.dispatch({ type: 'POP' });
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </Modal>
  );
}

export { ConfirmationModal };
