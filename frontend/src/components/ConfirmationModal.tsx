import React, { useContext, useRef } from 'react';
import { ConfirmationModal as ConfirmationModalType } from '../types';
import { Button1, Button2 } from '../components/Utils/Button';

function ConfirmationModal({
  title,
  message,
  onConfirm = () => {},
  onCancel = () => {},
  confirmText = 'Confirm',
  cancelText = 'Cancel',
}: ConfirmationModalType): JSX.Element {
  return (
    <div className="w-[300] flex flex-col space-y-4">
      <h3>{title}</h3>
      <p>{message}</p>
      <div className="flex flex-row justify-center space-x-2">
        <Button2
          className="flex-1"
          onClick={() => {
            onCancel();
          }}
        >
          {cancelText}
        </Button2>
        <Button1
          className="flex-1"
          onClick={() => {
            onConfirm();
          }}
        >
          {confirmText}
        </Button1>
      </div>
    </div>
  );
}

export { ConfirmationModal };
