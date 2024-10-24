import React from 'react';
import { InputTextBase, InputTextBaseInputProps } from './InputTextBase';
import { CheckOrX } from './CheckOrX';
import {
  useValidatedInputString,
  UseValidatedInputStringProps,
} from '../../utils/useValidatedInput';
import { Surface } from '../Utils/Surface';

type T = string;

interface ValidatedInputStringProps
  extends UseValidatedInputStringProps,
    InputTextBaseInputProps {
  showStatus?: boolean;
}

function ValidatedInputString({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  minLength,
  maxLength,
  showStatus = false,
  ...rest
}: ValidatedInputStringProps) {
  useValidatedInputString({
    state,
    setState,
    checkAvailability,
    checkValidity,
    isValid,
    isAvailable,
    minLength,
    maxLength,
  });

  return (
    <Surface>
      <div className="flex flex-row items-center space-x-2 input-text-container">
        <InputTextBase
          value={state.value}
          setValue={(value) =>
            setState((prev) => ({ ...prev, value: value as T }))
          }
          {...rest}
        />
        {showStatus && (
          <span title={state.error || ''}>
            <CheckOrX status={state.status} />
          </span>
        )}
      </div>
    </Surface>
  );
}

export { ValidatedInputString, ValidatedInputStringProps };
