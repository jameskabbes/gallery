import { ValidityCheckReturn } from '../Form/InputText';

function isPasswordValid(password: string): ValidityCheckReturn {
  return { valid: true };
}

export { isPasswordValid };
