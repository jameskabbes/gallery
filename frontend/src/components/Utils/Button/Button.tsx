import React from 'react';
import { UtilPatternProps } from '../../../types';
import { Surface } from '../Surface';

type ButtonProps = UtilPatternProps<'button'>;

function Button({ children, className = '', ...rest }: ButtonProps) {
  return (
    <Surface>
      <button className={`button-base ${className}`} {...rest}>
        {children}
      </button>
    </Surface>
  );
}

export default Button;
export { ButtonProps };
