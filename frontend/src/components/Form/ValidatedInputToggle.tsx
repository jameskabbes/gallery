import React, { useState, useEffect } from 'react';
import {
  InputCheckboxBase,
  InputCheckboxBaseInputProps,
  InputCheckboxBaseProps,
} from './InputCheckboxBase';
import {
  useValidatedInput,
  UseValidatedInputProps,
} from '../../utils/useValidatedInput';
import { Toggle1, ToggleProps } from '../Utils/Toggle';
import { CheckOrX } from './CheckOrX';

type T = boolean;

export interface ValidatedInputToggleProps extends UseValidatedInputProps<T> {
  toggleProps?: Omit<ToggleProps, 'state' | 'onClick' | 'children'>;
  inputProps?: Omit<
    InputCheckboxBaseProps,
    'checked' | 'setChecked' | 'className'
  >;
  showStatus?: boolean;
}

export function ValidatedInputToggle({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  toggleProps = {},
  inputProps = {},
  showStatus = false,
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
        {...toggleProps}
      >
        <InputCheckboxBase
          checked={state.value}
          setChecked={(value) => setState((prev) => ({ ...prev, value }))}
          className="opacity-0 absolute h-0 w-0 inset-0"
          {...inputProps}
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
