import React, { useContext, useRef, useEffect } from 'react';
import { ConfirmationModal as ConfirmationModalType } from '../types';
import { Button1, Button2 } from '../components/Utils/Button';

function ConfirmationModal({
  title,
  message,
  onConfirm = () => {},
  onCancel = () => {},
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  showCancel = true,
}: ConfirmationModalType): JSX.Element {
  const confirmButtonRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (confirmButtonRef.current) {
      confirmButtonRef.current.focus();
    }
  }, []);

  return (
    <form className="flex flex-col space-y-8">
      <header>{title}</header>
      <p className="break-words">{message}</p>
      <div className="flex flex-row justify-center space-x-2">
        {showCancel && (
          <Button2
            className="flex-1"
            onClick={() => {
              onCancel();
            }}
          >
            {cancelText}
          </Button2>
        )}
        <Button1
          className="flex-1"
          ref={confirmButtonRef}
          onClick={(e) => {
            e.preventDefault();
            onConfirm();
          }}
        >
          {confirmText}
        </Button1>
      </div>
    </form>
  );
}

export { ConfirmationModal };
