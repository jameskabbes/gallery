import React, { useState, useEffect } from 'react';

import { defaultInputState, InputState, InputStateAny } from '../../types';
import {
  BaseInputProps,
  Input,
  InputProps,
  ValidityCheckReturn,
} from './Input';

import { isDatetimeValid } from '../../services/isDatetimeValid';
import { InputText, InputTextProps } from './InputText';

interface InputDatetimeLocalProps {
  state: InputStateAny<Date>;
  setState: (state: InputStateAny<Date>) => void;
  id: string;
  checkValidity?: boolean;
  checkAvailability?: boolean;
  isValid?: (value: InputState<string>['value']) => ValidityCheckReturn;
  isAvailable?: (value: InputState<string>['value']) => Promise<boolean>;
  required?: boolean;
  className?: string;
}

function InputDatetimeLocal({
  state,
  setState,
  id,
  isValid = (value: InputState<string>['value']) => ({ valid: true }),

  ...rest
}: InputDatetimeLocalProps) {
  const [stringState, setStringState] = useState<InputState<string>>({
    ...defaultInputState<string>(''),
  });

  function isValidWrapper(
    value: InputState<string>['value']
  ): ValidityCheckReturn {
    return isValid(value) && isDatetimeValid(value);
  }

  useEffect(() => {
    if (state.value) {
      const newStringStateValue = new Date(
        state.value.getTime() - state.value.getTimezoneOffset() * 60000
      )
        .toISOString()
        .slice(0, 16);

      if (stringState.value !== newStringStateValue) {
        setStringState({
          ...stringState,
          value: newStringStateValue,
        });
      }
    }
  }, [state.value]);

  useEffect(() => {
    if (stringState.value) {
      const { valid } = isDatetimeValid(stringState.value);
      if (valid) {
        const newStateValue = new Date(stringState.value);
        if (state.value !== newStateValue) {
          setState({
            ...state,
            value: newStateValue,
          });
        }
      }
    }
  }, [stringState.value]);

  return (
    <InputText
      state={stringState}
      setState={setStringState}
      type={'datetime-local'}
      id={id}
      checkValidity={true}
      isValid={isValidWrapper}
      {...rest}
    />
  );
}

export { InputDatetimeLocal };
