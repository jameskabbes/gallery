import React, { useContext, useRef } from 'react';
import { ConfirmationModal as ConfirmationModalType } from '../types';

function ConfirmationModal({
  title,
  message,
  onConfirm = () => {},
  onCancel = () => {},
  confirmText = 'Confirm',
  cancelText = 'Cancel',
}: ConfirmationModalType): JSX.Element {
  return (
    <div className="max-w-[300]">
      <h3>{title}</h3>
      <p>{message}</p>
      <div className="flex flex-row justify-center space-x-2">
        <button
          className="button-secondary"
          onClick={() => {
            onCancel();
          }}
        >
          {cancelText}
        </button>
        <button
          className="button-primary"
          onClick={() => {
            onConfirm();
          }}
        >
          {confirmText}
        </button>
      </div>
    </div>
  );
}

export { ConfirmationModal };
