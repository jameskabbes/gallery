import React from 'react';
import { Surface } from '../Surface';

type LoaderProps = React.HTMLAttributes<HTMLSpanElement>;

function Loader({ children, className = '', ...rest }: LoaderProps) {
  return (
    <Surface>
      <span className={`loader-base ${className}`} {...rest}></span>
    </Surface>
  );
}

export default Loader;
export { LoaderProps };
