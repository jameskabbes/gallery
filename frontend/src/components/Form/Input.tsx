import React, { useEffect, useRef } from 'react';
import { InputState, InputValue } from '../../types';

interface ValidityCheckReturn {
  valid: boolean;
  message?: string;
}

interface BaseInputProps<T> {
  state: InputState<T>;
  setState: React.Dispatch<React.SetStateAction<InputState<T>>>;
  id: string;
  type: string;
  checkValidity?: boolean;
  checkAvailability?: boolean;
  isValid?: (value: InputState<T>['value']) => ValidityCheckReturn;
  isAvailable?: (value: InputState<T>['value']) => Promise<boolean>;
  required?: boolean;
  className?: string;
  value?: InputValue;
  checked?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

interface InputProps<T> extends BaseInputProps<T> {
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

function Input<T>({
  state,
  setState,
  id,
  type,
  onChange,
  checkValidity = false,
  checkAvailability = false,
  isValid = (value: InputState<T>['value']) => ({ valid: true }),
  isAvailable = async (value: InputState<T>['value']) => true,
  required = false,
  className = '',
  children = null,
  ...rest
}: InputProps<T>) {
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
    if (checkValidity) {
      const { valid, message } = isValid(state.value);
      setState({
        ...state,
        status: valid ? 'valid' : 'invalid',
        error: valid ? null : message,
      });
    }
  }, [state.value]);

  useEffect(() => {
    // see if the value is valid
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

    // see if the value is available
    if (!checkAvailability) {
      setState({
        ...state,
        status: 'valid',
        error: null,
      });
      return;
    }

    // check availability
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
    <>
      <input
        className={`${className} dark:[color-scheme:dark]`}
        type={type}
        id={id}
        required={required}
        onChange={onChange}
        {...rest}
      />
      {children}
    </>
  );
}

export { Input, BaseInputProps, InputProps, ValidityCheckReturn };
