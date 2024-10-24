import React, { useState, useEffect } from 'react';
import {
  InputCheckboxBase,
  InputCheckboxBaseInputProps,
} from './InputCheckboxBase';
import {
  useValidatedInput,
  UseValidatedInputProps,
} from '../../utils/useValidatedInput';
import { Toggle1 } from '../Utils/Toggle';
import { CheckOrX } from './CheckOrX';

type T = boolean;

interface ValidatedInputToggleProps
  extends UseValidatedInputProps<T>,
    InputCheckboxBaseInputProps {
  showStatus?: boolean;
}

function ValidatedInputToggle({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  showStatus = false,
  ...rest
}: ValidatedInputToggleProps) {
  useValidatedInput<T>({
    state,
    setState,
    checkAvailability,
    checkValidity,
    isValid,
    isAvailable,
  });

  return (
    <div className="flex flex-row items-center space-x-2">
      <Toggle1
        state={state.value}
        onClick={() => setState((prev) => ({ ...prev, value: !prev.value }))}
      >
        <InputCheckboxBase
          checked={state.value}
          setChecked={(value) => setState((prev) => ({ ...prev, value }))}
          className="opacity-0 absolute h-0 w-0 inset-0"
          {...rest}
        />
      </Toggle1>
      {showStatus && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { ValidatedInputToggle, ValidatedInputToggleProps };
