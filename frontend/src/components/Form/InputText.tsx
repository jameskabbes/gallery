import React, { useEffect, useRef } from 'react';
import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, ValidityCheckReturn } from './Input';
import { Surface } from '../Utils/Surface';

type T = string;

interface InputTextProps extends BaseInputProps<T> {
  minLength?: number | null;
  maxLength?: number | null;
  label?: string | null;
  placeholder?: string | null;
  showValidity?: boolean;
}

function InputText({
  state,
  setState,
  minLength = null,
  maxLength = null,
  label = null,
  placeholder = null,
  showValidity = true,
  isValid = (value: InputTextProps['state']['value']) => ({ valid: true }),
  ...rest
}: InputTextProps) {
  function isValidWrapper(
    value: InputState<string>['value']
  ): ValidityCheckReturn {
    if (minLength && value.length < minLength) {
      return {
        valid: false,
        message: `Must be at least ${minLength} characters`,
      };
    }
    if (maxLength && value.length > maxLength) {
      return {
        valid: false,
        message: `Must be at most ${maxLength} characters`,
      };
    }
    return isValid(value);
  }

  return (
    <Surface className="flex flex-row items-center space-x-2 input-text-container">
      <Input
        state={state}
        setState={setState}
        value={state.value}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          setState({
            ...state,
            value: e.target.value,
          });
        }}
        isValid={isValidWrapper}
        {...rest}
      />
      <div className="flex-1">
        {showValidity && (
          <span title={state.error || ''}>
            <CheckOrX status={state.status} />
          </span>
        )}
      </div>
    </Surface>
  );
}

export { InputText, InputTextProps };
