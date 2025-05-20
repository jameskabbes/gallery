import React, { useContext, useRef, useEffect } from 'react';
import { Button1, Button2 } from '../Utils/Button';

export interface ButtonConfirmationModalProps {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export function ButtonConfirmationModal({
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  showCancel = true,
  onConfirm = () => {},
  onCancel = () => {},
}: ButtonConfirmationModalProps): JSX.Element {
  const confirmButtonRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (confirmButtonRef.current) {
      confirmButtonRef.current.focus();
    }
  }, []);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onConfirm();
      }}
      className="flex flex-col space-y-8"
    >
      <header>{title}</header>
      <p className="break-words">{message}</p>
      <div className="flex flex-row justify-center space-x-2">
        {showCancel && (
          <Button2
            type="reset"
            className="flex-1"
            onClick={() => {
              onCancel();
            }}
          >
            {cancelText}
          </Button2>
        )}
        <Button1 type="submit" className="flex-1" ref={confirmButtonRef}>
          {confirmText}
        </Button1>
      </div>
    </form>
  );
}
