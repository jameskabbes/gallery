import validator from 'validator';

interface Return {
  valid: boolean;
  message?: string;
}

function isUsernameValid(username: string): Return {
  if (username.length < 1) {
    return { valid: false, message: 'Username is too short' };
  } else if (username.length > 100) {
    return { valid: false, message: 'Username is too long' };
  } else if (!validator.isAlphanumeric(username)) {
    return { valid: false, message: 'Username must be alphanumeric' };
  } else {
    return { valid: true };
  }
}

export { isUsernameValid };
