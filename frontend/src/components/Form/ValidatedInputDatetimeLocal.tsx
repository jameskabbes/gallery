import React, { useState, useEffect } from 'react';
import { isDatetimeValid } from '../../services/isDatetimeValid';
import { CheckOrX } from './CheckOrX';

import { InputTextBase, InputTextBaseInputProps } from './InputTextBase';
import {
  useValidatedInput,
  UseValidatedInputProps,
} from '../../utils/useValidatedInput';
import { Surface } from '../Utils/Surface';

type T = Date;

interface ValidatedInputDatetimeLocalProps
  extends UseValidatedInputProps<T>,
    InputTextBaseInputProps {
  showStatus?: boolean;
}

function ValidatedInputDatetimeLocal({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  showStatus = true,
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
        <InputTextBase
          value={dateString}
          setValue={(value: string) => {
            setDateString(value);
            const checkValidReturn = isDatetimeValid(value);

            if (checkValidReturn.valid) {
              setState({
                ...state,
                value: new Date(value),
                status: 'valid',
                error: null,
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

export { ValidatedInputDatetimeLocal, ValidatedInputDatetimeLocalProps };
