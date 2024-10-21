import React from 'react';
import Button, { ButtonProps } from './Button';
import { Surface } from '../Surface';

function Button2({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Surface>
      <Button className={'border-[1px] ' + className} {...rest}>
        {children}
      </Button>
    </Surface>
  );
}

export default Button2;
