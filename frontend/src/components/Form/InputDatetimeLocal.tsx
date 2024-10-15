import React, { useState, useEffect } from 'react';

import { defaultInputState, InputState, InputStateAny } from '../../types';
import {
  BaseInputProps,
  Input,
  InputProps,
  ValidityCheckReturn,
} from './Input';

import { isDatetimeValid } from '../../services/isDatetimeValid';
import { InputText } from './InputText';

interface InputDatetimeLocalProps {
  state: InputStateAny<Date>;
  setState: (state: InputStateAny<Date>) => void;
  id: string;
}

function convertToLocalDate(date: Date) {
  const newDate = new Date(
    date.getTime() - date.getTimezoneOffset() * 60 * 1000
  );
  return newDate;
}

function InputDatetimeLocal({ state, setState, id }: InputDatetimeLocalProps) {
  const [stringState, setStringState] = useState<InputState<string>>({
    ...defaultInputState<string>(''),
  });

  console.log('state', state);

  useEffect(() => {
    if (state.value) {
      const newStringStateValue = convertToLocalDate(state.value)
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
      isValid={isDatetimeValid}
    />
  );
}

export { InputDatetimeLocal };
