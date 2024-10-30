import { ValidatedInputCheckValidityReturn } from '../utils/useValidatedInput';

function isPasswordValid(password: string): ValidatedInputCheckValidityReturn {
  return { valid: true };
}

export { isPasswordValid };
