import React, {
  ElementType,
  ComponentPropsWithRef,
  useMemo,
  forwardRef,
  isValidElement,
  cloneElement,
} from 'react';
import { useSurface, getNextSurface } from '../../utils/useSurface';
import { SurfaceContext, useSurfaceContext } from '../../contexts/Surface';
import { SurfaceContextValue } from '../../types';

import { MutableRefObject, RefCallback } from 'react';

function combineRefs<T>(
  ...refs: (MutableRefObject<T> | RefCallback<T> | null)[]
): RefCallback<T> {
  return (element: T) => {
    refs.forEach((ref) => {
      if (typeof ref === 'function') {
        ref(element);
      } else if (ref) {
        (ref as MutableRefObject<T | null>).current = element;
      }
    });
  };
}

export { combineRefs };

interface Props<T extends ElementType> {
  overrideMode?: SurfaceContextValue['mode'] | null;
  as?: T;
  children?: React.ReactNode;
}

const Surface = forwardRef(
  <T extends ElementType = 'div'>(
    {
      overrideMode = null,
      as: Tag = 'div',
      children,
      ...props
    }: Props<T> & ComponentPropsWithRef<T>,
    ref: React.Ref<Element>
  ) => {
    const parentSurface = useSurfaceContext();
    const surface = getNextSurface(parentSurface, overrideMode);
    const surfaceRef = useSurface(surface);
    const contextValue = useMemo<SurfaceContextValue>(() => surface, [surface]);

    return (
      <SurfaceContext.Provider value={contextValue}>
        {isValidElement(children)
          ? cloneElement(children, {
              ref: combineRefs(ref, surfaceRef, (children as any).ref),
              ...props,
            })
          : children}
      </SurfaceContext.Provider>
    );
  }
);

export { Surface };
