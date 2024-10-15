import { ValidityCheckReturn } from '../../components/Form/Input';

function isPasswordValid(password: string): ValidityCheckReturn {
  return { valid: true };
}

export { isPasswordValid };
