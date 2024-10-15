import validator from 'validator';
import openapi_schema from '../../../../openapi_schema.json';
import { ValidityCheckReturn } from '../../components/Form/Input';

function isUsernameValid(username: string): ValidityCheckReturn {
  if (!validator.isAlphanumeric(username)) {
    return { valid: false, message: 'Username must be alphanumeric' };
  } else {
    return { valid: true };
  }
}

export { isUsernameValid };
