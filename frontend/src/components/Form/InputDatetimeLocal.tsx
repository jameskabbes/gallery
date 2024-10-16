import React, { useState, useEffect } from 'react';

import { defaultInputState, InputState } from '../../types';
import {
  BaseInputProps,
  Input,
  InputProps,
  ValidityCheckReturn,
} from './Input';

import { isDatetimeValid } from '../../services/isDatetimeValid';
import { InputText, InputTextProps } from './InputText';

type T = Date;

interface InputDatetimeLocalProps extends BaseInputProps<T> {}

function InputDatetimeLocal({
  state,
  setState,
  checkValidity = true,
  ...rest
}: InputDatetimeLocalProps) {
  const [stringState, setStringState] = useState<InputState<string>>({
    ...defaultInputState<string>(''),
  });

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
      checkValidity={checkValidity}
      {...rest}
    />
  );
}

export { InputDatetimeLocal };
