import React from 'react';
import Button1 from './Button1';
import { ButtonProps } from './Button';

function ButtonSubmit({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Button1
      type="submit"
      className="flex flex-row justify-center p-4 rounded-3xl mb-0"
    >
      {children}
    </Button1>
  );
}

export default ButtonSubmit;
