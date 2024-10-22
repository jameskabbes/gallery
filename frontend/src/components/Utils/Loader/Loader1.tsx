import React from 'react';
import Loader, { LoaderProps } from './Loader';

function Loader1({ className = '', ...rest }: LoaderProps) {
  return <Loader className={`loader1 ${className}`} {...rest} />;
}

export default Loader1;
