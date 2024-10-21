import React from 'react';
import Button, { ButtonProps } from './Button';

function Button1({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Button
      className="bg-primary-light dark:bg-primary-dark  text-light-lighter"
      {...rest}
    >
      {children}
    </Button>
  );
}

export default Button1;
