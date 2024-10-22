import React from 'react';
import { UtilPatternProps } from '../../../types';

function Button1({
  children,
  className = '',
  ...rest
}: UtilPatternProps<'button'>) {
  return (
    <button
      className={`button-base bg-primary-light dark:bg-primary-dark  text-light-lighter ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

export default Button1;
