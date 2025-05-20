import { ValidatedInputCheckValidityReturn } from '../utils/useValidatedInput';

export function isDatetimeValid(
  value: string
): ValidatedInputCheckValidityReturn {
  const date = new Date(value);
  if (isNaN(date.getTime())) {
    return { valid: false, message: 'Invalid date' };
  } else {
    return { valid: true };
  }
}
