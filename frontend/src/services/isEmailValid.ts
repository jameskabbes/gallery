import validator from 'validator';
import { ValidatedInputCheckValidityReturn } from '../utils/useValidatedInput';

export function isEmailValid(email: string): ValidatedInputCheckValidityReturn {
  if (!validator.isEmail(email)) {
    return { valid: false, message: 'Invalid email' };
  } else {
    return { valid: true };
  }
}
