import React, { useContext, useState, useRef, useEffect } from 'react';
import { defaultValidatedInputState, ValidatedInputState } from '../../types';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ButtonSubmit } from '../Utils/Button';
import { Surface } from '../Utils/Surface';
import { Card1 } from '../Utils/Card';

export interface TextConfirmationModalProps {
  title: string;
  message: React.ReactNode;
  target: string;
  confirmText?: string;
  onConfirm?: () => void;
}

export function TextConfirmationModal({
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
      className="flex flex-col space-y-6"
    >
      <header className="mb-4">{title}</header>
      {message}

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
      <p className="text-center">
        To proceed, type{' '}
        <code>
          <strong>{target}</strong>
        </code>{' '}
        in the field above.
      </p>
      <ButtonSubmit disabled={confirm.status !== 'valid'}>
        {confirmText}
      </ButtonSubmit>
    </form>
  );
}
