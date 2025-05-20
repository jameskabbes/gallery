import { ValidatedInputCheckValidityReturn } from '../utils/useValidatedInput';

export function isPasswordValid(
  password: string
): ValidatedInputCheckValidityReturn {
  return { valid: true };
}
