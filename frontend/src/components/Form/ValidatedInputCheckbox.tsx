import React from 'react';
import {
  InputCheckboxBase,
  InputCheckboxBaseInputProps,
} from './InputCheckboxBase';
import { Checkbox1 } from '../Utils/Checkbox';
import { CheckOrX } from './CheckOrX';
import {
  useValidatedInput,
  UseValidatedInputProps,
} from '../../utils/useValidatedInput';

type T = boolean;

export interface ValidatedInputCheckboxProps
  extends UseValidatedInputProps<T>,
    InputCheckboxBaseInputProps {
  showStatus?: boolean;
}

export function ValidatedInputCheckbox({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  showStatus = false,
  ...rest
}: ValidatedInputCheckboxProps) {
  useValidatedInput<T>({
    state,
    setState,
    checkAvailability,
    checkValidity,
    isValid,
    isAvailable,
  });

  return (
    <div className="relative flex flex-row items-center space-x-2">
      <Checkbox1
        state={state.value}
        onClick={() => setState((prev) => ({ ...prev, value: !prev.value }))}
      >
        <InputCheckboxBase
          checked={state.value}
          setChecked={(value) => setState((prev) => ({ ...prev, value }))}
          className="opacity-0 absolute h-0 w-0 inset-0"
          {...rest}
        />
      </Checkbox1>
      {showStatus && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}
