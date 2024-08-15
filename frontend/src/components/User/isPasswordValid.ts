interface Return {
  valid: boolean;
  message?: string;
}

function isPasswordValid(password: string): Return {
  if (password.length < 1) {
    return { valid: false, message: 'Password is too short' };
  }
  return { valid: true };
}

export { isPasswordValid };
