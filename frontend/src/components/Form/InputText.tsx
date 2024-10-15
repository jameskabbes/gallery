import React, { useEffect, useRef } from 'react';
import { CheckOrX } from './CheckOrX';
import { InputState, Input as InputType } from '../../types';
import {
  BaseInputProps,
  Input,
  InputProps,
  ValidityCheckReturn,
} from './Input';

interface InputTextProps extends BaseInputProps<string> {
  state: InputProps<string>['state'];
  setState: InputProps<string>['setState'];
  type: InputProps<string>['type'];
  minLength?: number | null;
  maxLength?: number | null;
  label?: string | null;
  placeholder?: string | null;
  showValidity?: boolean;
}

function InputText({
  state,
  setState,
  id,
  type,
  minLength = null,
  maxLength = null,
  label = null,
  placeholder = null,
  showValidity = true,
  isValid = (value: InputState<string>['value']) => ({ valid: true }),
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
    <div className="flex flex-row items-center space-x-2 text-input">
      <Input
        state={state}
        setState={setState}
        type={type}
        id={id}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          let newValue: InputState<string>['value'] = e.target.value;
          setState({
            ...state,
            value: newValue,
          });
        }}
        isValid={isValidWrapper}
        {...rest}
      />
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputText, InputTextProps };
