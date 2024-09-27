import validator from 'validator';
import openapi_schema from '../../../../openapi_schema.json';
import { ValidityCheckReturn } from '../../components/Form/InputText';

function isEmailValid(email: string): ValidityCheckReturn {
  if (!validator.isEmail(email)) {
    return { valid: false, message: 'Invalid email' };
  } else {
    return { valid: true };
  }
}

export { isEmailValid };
