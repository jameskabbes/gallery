import React from 'react';
import Loader, { LoaderProps } from './Loader';

function Loader2({ className = '', ...rest }: LoaderProps) {
  return <Loader className={`loader2 ${className}`} {...rest} />;
}

export default Loader2;
