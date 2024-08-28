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
  label?: string | null;
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
  label = null,
  type = 'text',
  placeholder = null,
  showValidity = true,
  checkAvailability = false,
  isAvailable = async (value: InputState['value']) => true,
  isValid = (value: InputState['value']) => ({ valid: true }),
  required = true,
}: Props<T>) {
  const debounceTimeout = useRef(null);

  async function checkAvailabilityApi() {
    let available = await isAvailable(state.value);
    setState({
      ...state,
      status: available ? 'valid' : 'invalid',
      error: available ? null : `Not available`,
    });
  }

  useEffect(() => {
    if (state.value.length < minLength) {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      setState({
        ...state,
        status: 'invalid',
        error: `Must be at least ${minLength} characters`,
      });
      return;
    }
    // too long
    if (state.value.length > maxLength) {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
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
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      setState({
        ...state,
        status: 'invalid',
        error: message,
      });
      return;
    }

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
    }, 300);
  }, [state.value]);

  return (
    <div className="flex flex-row items-center space-x-2">
      {label && <label htmlFor={id}>{label}</label>}
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
