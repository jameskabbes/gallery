import React, { useEffect, useRef } from 'react';
import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, ValidityCheckReturn } from './Input';
import { Surface } from '../Utils/Surface';

type T = string;

interface InputTextBaseProps extends BaseInputProps<T> {
  minLength?: number | null;
  maxLength?: number | null;
}

function InputTextBase({
  state,
  setState,
  minLength = null,
  maxLength = null,
  isValid = (value: InputTextBaseProps['state']['value']) => ({ valid: true }),
  ...rest
}: InputTextBaseProps) {
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
  );
}

export { InputTextBase, InputTextBaseProps };
