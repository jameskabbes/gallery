import React from 'react';
import Button, { ButtonProps } from './Button';

function Button3({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Button
      className={`button-base bg-color-invert text-color-invert  ${className}`}
      {...rest}
    >
      {children}
    </Button>
  );
}

export default Button3;
