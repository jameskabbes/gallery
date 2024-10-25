import React, { useContext, useRef, useEffect } from 'react';
import { ConfirmationModal as ConfirmationModalType } from '../types';
import { Button1, Button2 } from '../components/Utils/Button';

function ConfirmationModal({
  title,
  message,
  onConfirm = () => {},
  onCancel = () => {},
  confirm = 'Confirm',
  cancel = 'Cancel',
  showCancel = true,
}: ConfirmationModalType): JSX.Element {
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    confirmButtonRef.current?.focus();
  }, [confirmButtonRef.current]);

  return (
    <form className="flex flex-col">
      <header>{title}</header>
      <p>{message}</p>
      <div className="flex flex-row justify-center space-x-2">
        {showCancel && (
          <Button2
            className="flex-1"
            onClick={() => {
              onCancel();
            }}
          >
            {cancel}
          </Button2>
        )}
        <Button1
          ref={confirmButtonRef}
          className="flex-1"
          onClick={() => {
            onConfirm();
          }}
        >
          {confirm}
        </Button1>
      </div>
    </form>
  );
}

export { ConfirmationModal };
