import React, { useEffect, useRef } from 'react';
import { CheckOrX } from './CheckOrX';
import { InputState, InputStatus } from '../../types';

const defaultInputState: InputState = {
  value: '',
  status: 'invalid',
  error: null,
};

interface ValidityCheckReturn {
  valid: boolean;
  message?: string;
}

interface Props<T> {
  state: InputState;
  setState: (state: InputState) => void;
  id: string;
  minLength: number;
  maxLength: number;
  type?: string;
  placeholder?: string;
  showValidity?: boolean;
  checkAvailability?: boolean;
  isValid?: (value: InputState['value']) => {
    valid: boolean;
    message?: string;
  };
  isAvailable?: (value: InputState['value']) => Promise<boolean>;
  required?: boolean;
}

function InputText<T>({
  state,
  setState,
  id,
  minLength,
  maxLength,
  type = 'text',
  placeholder = null,
  showValidity = true,
  checkAvailability = false,
  isAvailable = async (value: InputState['value']) => true,
  isValid = (value: InputState['value']) => ({ valid: true }),
  required = true,
}: Props<T>) {
  const debounceTimeout = useRef(null);

  useEffect(() => {
    verifyPipeline();
  }, [state.value]);

  async function checkAvailabilityApi() {
    let available = await isAvailable(state.value);
    setState({
      ...state,
      status: available ? 'valid' : 'invalid',
      error: available ? null : `Not available`,
    });

    setState({
      ...state,
      status: available ? 'valid' : 'invalid',
      error: available ? null : `Not available`,
    });
  }

  function verifyPipeline() {
    // too short
    if (state.value.length < minLength) {
      setState({
        ...state,
        status: 'invalid',
        error: `Must be at least ${minLength} characters`,
      });
      return;
    }
    // too long
    if (state.value.length > maxLength) {
      setState({
        ...state,
        status: 'invalid',
        error: `Must be at most ${maxLength} characters`,
      });
      return;
    }
    // otherwise invalid
    const { valid, message } = isValid(state.value);
    if (!valid) {
      setState({
        ...state,
        status: 'invalid',
        error: message,
      });
      return;
    }
    // check availability?
    if (!checkAvailability) {
      setState({
        ...state,
        status: 'valid',
        error: null,
      });
      return;
    }

    setState({
      ...state,
      status: 'loading',
      error: null,
    });

    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      checkAvailabilityApi();
    }, 200);
  }

  return (
    <div className="flex flex-row items-center space-x-2">
      <input
        className="text-input"
        type={type}
        id={id}
        value={state.value}
        placeholder={placeholder}
        onChange={(e) => {
          let newValue: InputState['value'] = e.target.value;
          setState({
            ...state,
            value: newValue,
          });
        }}
        required={required}
        minLength={minLength}
        maxLength={maxLength}
      />
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { defaultInputState, ValidityCheckReturn, InputText };
