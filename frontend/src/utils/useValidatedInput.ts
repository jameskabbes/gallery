import { useEffect, useRef } from 'react';
import { ValidatedInputState } from '../types';
import siteConfig from '../../siteConfig.json';

interface ValidatedInputCheckValidityReturn {
  valid: boolean;
  message?: string;
}

interface UseValidatedInputProps<T> {
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

function useValidatedInput<T>({
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
      setState({
        ...state,
        status: valid ? 'valid' : 'invalid',
        error: valid ? null : message,
      });

      // if the value is not valid, cancel pending request, return immediately
      if (!valid) {
        if (debounceTimeout.current) {
          clearTimeout(debounceTimeout.current);
        }
        return;
      }
    }

    if (checkAvailability) {
      setState({
        ...state,
        status: 'loading',
        error: null,
      });

      // there is an existing timeout, but we want to reset it since we changed the value already
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      debounceTimeout.current = setTimeout(async () => {
        let available = await isAvailable(state.value);
        setState({
          ...state,
          status: available ? 'valid' : 'invalid',
          error: available ? null : `Not available`,
        });
      }, siteConfig.validatedInput.debounceTimeoutLength);
    }
  }, [state.value]);
}

interface UseValidatedInputStringProps extends UseValidatedInputProps<string> {
  minLength?: number | null;
  maxLength?: number | null;
}

function useValidatedInputString({
  isValid = (value) => ({ valid: true }),
  minLength = null,
  maxLength = null,
  ...rest
}: UseValidatedInputStringProps) {
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
    return isValid(value);
  }

  return useValidatedInput<string>({ isValid: isValidWrapper, ...rest });
}

export {
  ValidatedInputCheckValidityReturn,
  useValidatedInput,
  UseValidatedInputProps,
  useValidatedInputString,
  UseValidatedInputStringProps,
};
