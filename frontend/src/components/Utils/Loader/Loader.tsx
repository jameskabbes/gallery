import React from 'react';
import { UtilPatternProps } from '../../../types';
import { Surface } from '../Surface';

type LoaderProps = UtilPatternProps<'span'>;

function Loader({ children, className = '', ...rest }: LoaderProps) {
  return (
    <Surface>
      <span className={`loader-base ${className}`} {...rest}></span>
    </Surface>
  );
}

export default Loader;
export { LoaderProps };
