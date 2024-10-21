import React from 'react';
import { ButtonProps } from './Button';
import Button1 from './Button1';

function ButtonSubmit({ children }: ButtonProps) {
  return (
    <Button1
      type="submit"
      className="bg-primary-light dark:bg-primary-dark text-light-lighter"
    >
      {children}
    </Button1>
  );
}

export default ButtonSubmit;
