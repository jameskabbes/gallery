import validator from 'validator';

interface Return {
  valid: boolean;
  message?: string;
}

function isEmailValid(email: string): Return {
  if (!validator.isEmail(email)) {
    return { valid: false, message: 'Invalid email' };
  } else if (email.length > 100) {
    return { valid: false, message: 'Email is too long' };
  } else {
    return { valid: true };
  }
}

export { isEmailValid };
