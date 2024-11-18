import React, { useContext, useState, useRef, useEffect } from 'react';
import {
  ConfirmationModalBaseProps,
  defaultValidatedInputState,
  ValidatedInputState,
} from '../../types';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ButtonSubmit } from '../Utils/Button';

interface TextConfirmationModalProps extends ConfirmationModalBaseProps {
  title: string;
  message: React.ReactNode;
  target: string;
  confirmText?: string;
}

function TextConfirmationModal({
  title,
  message,
  target,
  confirmText = 'Confirm',
  onConfirm = () => {},
}: TextConfirmationModalProps): JSX.Element {
  const [confirm, setConfirm] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onConfirm();
      }}
      className="flex flex-col space-y-8"
    >
      <header>{title}</header>
      {message}
      <p className="text-center">
        To proceed, type{' '}
        <code>
          <strong>{target}</strong>
        </code>{' '}
        in the field below.
      </p>
      <ValidatedInputString
        state={confirm}
        setState={setConfirm}
        checkValidity={true}
        isValid={(value) =>
          value === target
            ? { valid: true }
            : { valid: false, message: 'Input does not match target' }
        }
      />
      <ButtonSubmit disabled={confirm.status !== 'valid'}>
        {confirmText}
      </ButtonSubmit>
    </form>
  );
}

export { TextConfirmationModal, TextConfirmationModalProps };
