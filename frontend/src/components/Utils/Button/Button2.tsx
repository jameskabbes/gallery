import React from 'react';
import Button, { ButtonProps } from './Button';

function Button2({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Button className={`button-base border-[1px] ${className}`} {...rest}>
      {children}
    </Button>
  );
}

export default Button2;
