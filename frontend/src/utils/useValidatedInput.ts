import { useEffect, useRef } from 'react';
import { ValidatedInputState } from '../types';
import { validatedInput } from '../config/constants';

export interface ValidatedInputCheckValidityReturn {
  valid: boolean;
  message?: string;
}

export interface UseValidatedInputProps<T> {
  state: ValidatedInputState<T>;
  setState: React.Dispatch<
    React.SetStateAction<UseValidatedInputProps<T>['state']>
  >;
  checkValidity?: boolean;
  checkAvailability?: boolean;
  isValid?: (
    value: UseValidatedInputProps<T>['state']['value']
  ) => ValidatedInputCheckValidityReturn;
  isAvailable?: (
    value: UseValidatedInputProps<T>['state']['value']
  ) => Promise<boolean>;
}

export function useValidatedInput<T>({
  state,
  setState,
  checkValidity = false,
  checkAvailability = false,
  isValid = (value) => ({ valid: true }),
  isAvailable = async (value) => true,
}: UseValidatedInputProps<T>) {
  const debounceTimeout = useRef(null);

  useEffect(() => {
    if (checkValidity) {
      const { valid, message } = isValid(state.value);
      setState((prev) => ({
        ...prev,
        status: valid ? 'valid' : 'invalid',
        error: valid ? null : message,
      }));

      // if the value is not valid, cancel pending request, return immediately
      if (!valid) {
        if (debounceTimeout.current) {
          clearTimeout(debounceTimeout.current);
        }
        return;
      }
    }

    if (checkAvailability) {
      setState((prev) => ({
        ...prev,
        status: 'loading',
        error: null,
      }));

      // there is an existing timeout, but we want to reset it since we changed the value already
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      debounceTimeout.current = setTimeout(async () => {
        let available = await isAvailable(state.value);
        setState((prev) => ({
          ...prev,
          status: available ? 'valid' : 'invalid',
          error: available ? null : `Not available`,
        }));
      }, validatedInput.debounceTimeoutLength);
    } else {
      // if we are not checking availability, clear the timeout
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    }

    // if we are not checking validity or availability, clear the timeout
  }, [state.value]);
}

export interface UseValidatedInputStringProps
  extends UseValidatedInputProps<string> {
  minLength?: React.InputHTMLAttributes<HTMLInputElement>['minLength'];
  maxLength?: React.InputHTMLAttributes<HTMLInputElement>['minLength'];
  pattern?: React.InputHTMLAttributes<HTMLInputElement>['pattern'];
}

export function useValidatedInputString({
  isValid = (value) => ({ valid: true }),
  minLength,
  maxLength,
  pattern,
  ...rest
}: UseValidatedInputStringProps) {
  const regexPattern = pattern ? new RegExp(pattern) : null;

  function isValidWrapper(value: string): ValidatedInputCheckValidityReturn {
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
    if (pattern && !regexPattern.test(value)) {
      return {
        valid: false,
        message: `Invalid format`,
      };
    }
    return isValid(value);
  }

  return useValidatedInput<string>({ isValid: isValidWrapper, ...rest });
}
