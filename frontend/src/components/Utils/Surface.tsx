import React, { ElementType, ComponentPropsWithRef, useMemo } from 'react';
import { useSurface } from '../../utils/useSurface';
import { SurfaceContext, useSurfaceContext } from '../../contexts/Surface';
import { SurfaceContextValue } from '../../types';

interface Props<T extends ElementType> {
  overrideMode?: SurfaceContextValue['mode'] | null;
  as?: T;
  children?: React.ReactNode;
  className?: string;
}

function Surface<T extends ElementType = 'div'>({
  overrideMode = null,
  as: Tag = 'div',
  children,
  className = '',
  ...props
}: Props<T> & ComponentPropsWithRef<T>) {
  const parentSurface = useSurfaceContext();
  const surface: SurfaceContextValue = {
    level: parentSurface.level + 1,
    mode: overrideMode
      ? overrideMode
      : parentSurface.mode === 'even'
      ? 'odd'
      : 'even',
  };

  const surfaceRef = useSurface(surface);
  const contextValue = useMemo<SurfaceContextValue>(() => surface, [surface]);

  return (
    <SurfaceContext.Provider value={contextValue}>
      <Tag ref={surfaceRef} className={className} {...props}>
        {children}
      </Tag>
    </SurfaceContext.Provider>
  );
}

export { Surface };
