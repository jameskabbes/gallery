import { ValidityCheckReturn } from '../components/Form/Input';

function isDatetimeValid(value: string): ValidityCheckReturn {
  const date = new Date(value);

  if (isNaN(date.getTime())) {
    return { valid: false, message: 'Invalid date' };
  } else {
    return { valid: true };
  }
}

export { isDatetimeValid };
