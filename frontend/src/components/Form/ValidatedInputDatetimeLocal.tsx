import React, { useState, useEffect } from 'react';
import { isDatetimeValid } from '../../services/isDatetimeValid';
import { CheckOrX } from './CheckOrX';

import { InputTextBase, InputTextBaseInputProps } from './InputTextBase';
import {
  useValidatedInput,
  UseValidatedInputProps,
} from '../../utils/useValidatedInput';
import { Surface } from '../Utils/Surface';

type T = Date | null;

export interface ValidatedInputDatetimeLocalProps
  extends UseValidatedInputProps<T>,
    Omit<InputTextBaseInputProps, 'type'> {
  showStatus?: boolean;
}

export function ValidatedInputDatetimeLocal({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  showStatus = true,
  className = '',
  ...rest
}: ValidatedInputDatetimeLocalProps) {
  useValidatedInput<T>({
    state,
    setState,
    checkAvailability,
    checkValidity,
    isValid,
    isAvailable,
  });

  const [dateString, setDateString] = useState<string>('');

  useEffect(() => {
    if (state.value) {
      setDateString(() => {
        return new Date(
          state.value.getTime() - state.value.getTimezoneOffset() * 60000
        )
          .toISOString()
          .slice(0, 16);
      });
    }
  }, [state.value]);

  return (
    <Surface>
      <div className="flex flex-row items-center justify-between space-x-2 input-datetime-local-container">
        <InputTextBase
          value={dateString}
          setValue={(value: string) => {
            setDateString(value);

            const checkValidReturn = isDatetimeValid(value);
            if (checkValidReturn.valid) {
              setState((prev) => ({
                ...prev,
                value: new Date(value),
                status: 'valid',
                error: null,
              }));
            } else {
              setState((prev) => ({
                ...prev,
                value: null,
                status: 'invalid',
                error: checkValidReturn.message,
              }));
            }
          }}
          type="datetime-local"
          className={'dark:[color-scheme:dark]' + className}
          {...rest}
        />
        <div>
          {showStatus && (
            <span title={state.error || ''}>
              <CheckOrX status={state.status} />
            </span>
          )}
        </div>
      </div>
    </Surface>
  );
}
