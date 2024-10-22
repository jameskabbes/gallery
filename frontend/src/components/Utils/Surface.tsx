import React from 'react';
import {
  useSurfaceProvider,
  UseSurfaceProviderProps,
} from '../../utils/useSurface';
import { SurfaceContext } from '../../contexts/Surface';
import combineRefs from '../../utils/combineRefs';

interface Props extends UseSurfaceProviderProps {
  children: React.ReactElement<any> & React.RefAttributes<any>; // Include ref attributes
}

function Surface({ overrideMode = null, children }: Props) {
  const { surfaceContextValue, surfaceRef } = useSurfaceProvider({
    overrideMode,
  });

  if (!React.isValidElement(children)) {
    console.error(
      'Surface component expects a single valid React element as a child.'
    );
    return null;
  }

  const child = React.Children.only(children);

  const combinedRef = combineRefs(surfaceRef, (child as any).ref); // Reference the actual child

  return (
    <SurfaceContext.Provider value={surfaceContextValue}>
      {React.cloneElement(child, {
        ref: combinedRef as any, // TypeScript casting
      })}
    </SurfaceContext.Provider>
  );
}

export { Surface };
