import React from 'react';
import { UtilPatternProps } from '../../../types';

type ButtonProps = UtilPatternProps<'button'>;

function Button({ children, className = '', ...rest }: ButtonProps) {
  return (
    <button className={`button-base ` + className} {...rest}>
      {children}
    </button>
  );
}

export default Button;
export type { ButtonProps };
