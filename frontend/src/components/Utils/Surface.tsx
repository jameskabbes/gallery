import React, {
  useState,
  useEffect,
  ElementType,
  ComponentPropsWithRef,
} from 'react';
import { useSurfaceLevel, SurfaceLevel } from '../../utils/useSurfaceLevel';

interface Props<T extends ElementType> {
  overrideSurfaceLevel?: SurfaceLevel | null;
  as?: T;
  children?: React.ReactNode;
  className?: string;
}

function Surface<T extends ElementType = 'div'>({
  overrideSurfaceLevel = null,
  as: Tag = 'div',
  children,
  className = '',
  ...props
}: Props<T> & ComponentPropsWithRef<T>) {
  const surfaceRef = useSurfaceLevel(overrideSurfaceLevel);
  return (
    <Tag ref={surfaceRef} className={`surface ${className}`} {...props}>
      {children}
    </Tag>
  );
}

export { Surface };
