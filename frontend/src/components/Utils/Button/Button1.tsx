import React from 'react';
import Button, { ButtonProps } from './Button';

function Button1({
  children,
  className = '',
  ...rest
}: ButtonProps) {
  return (
    <Button
      className={`button-base bg-primary-light dark:bg-primary-dark  text-light-lighter ${className}`}
      {...rest}
    >
      {children}
    </Button>
  );
}

export default Button1;
