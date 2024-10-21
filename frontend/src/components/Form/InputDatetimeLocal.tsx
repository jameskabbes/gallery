import React, { useState, useEffect } from 'react';
import { BaseInputProps, Input } from './Input';

import { isDatetimeValid } from '../../services/isDatetimeValid';
import { CheckOrX } from './CheckOrX';
import { Surface } from '../Utils/Surface';

type T = Date;

interface InputDatetimeLocalProps extends BaseInputProps<T> {
  showValidity?: boolean;
}

function InputDatetimeLocal({
  state,
  setState,
  showValidity = false,
  ...rest
}: InputDatetimeLocalProps) {
  const [dateString, setDateString] = useState<string>('');

  useEffect(() => {
    if (state.value) {
      setDateString(
        new Date(
          state.value.getTime() - state.value.getTimezoneOffset() * 60000
        )
          .toISOString()
          .slice(0, 16)
      );
    }
  }, [state.value]);

  return (
    <Surface>
      <div className="flex flex-row items-center space-x-2 input-datetime-local-container">
        <Input
          state={state}
          setState={setState}
          value={dateString}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const dateString = e.target.value;

            const checkValidReturn = isDatetimeValid(dateString);

            if (checkValidReturn.valid) {
              setState({
                ...state,
                value: new Date(dateString),
              });
            } else {
              setState({
                ...state,
                value: null,
                status: 'invalid',
                error: checkValidReturn.message,
              });
            }
          }}
          {...rest}
        />
        <div className="flex-1">
          {showValidity && showValidity == true && (
            <span title={state.error || ''}>
              <CheckOrX status={state.status} />
            </span>
          )}
        </div>
      </div>
    </Surface>
  );
}

export { InputDatetimeLocal };
