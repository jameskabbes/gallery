import React from 'react';
import { Surface } from '../Surface';
import { UtilPatternProps } from '../../../types';

function Button2({
  children,
  className = '',
  ...rest
}: UtilPatternProps<'button'>) {
  return (
    <Surface>
      <button className={'button-base border-[1px] ' + className} {...rest}>
        {children}
      </button>
    </Surface>
  );
}

export default Button2;
