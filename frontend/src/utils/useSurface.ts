import { useContext, useEffect, useRef, RefObject, useMemo } from 'react';
import { SurfaceContextType } from '../types';
import { SurfaceContext } from '../contexts/Surface';

export interface OverrideParentSurfaceProps {
  overrideMode?: SurfaceContextType['mode'] | null;
  keepParentMode?: boolean;
}

export function getNextSurface(
  surface: SurfaceContextType,
  overrideParentSurfaceProps: OverrideParentSurfaceProps
): SurfaceContextType {
  let mode: SurfaceContextType['mode'];

  if (overrideParentSurfaceProps.overrideMode) {
    mode = overrideParentSurfaceProps.overrideMode;
  } else if (overrideParentSurfaceProps.keepParentMode) {
    mode = surface.mode;
  } else {
    mode = surface.mode === 'a' ? 'b' : 'a';
  }

  return {
    level: surface.level + 1,
    mode: mode,
  };
}

export function useSurface<T extends HTMLElement>(
  surface: SurfaceContextType
): RefObject<T> {
  const ref = useRef<T>(null);
  useEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.setAttribute('data-surface-level', surface['level'].toString());
    element.setAttribute('data-surface-mode', surface['mode']);
  }, [surface]);

  return ref;
}

export function useSurfaceProvider<T extends HTMLElement>(
  overrideParentSurfaceProps: OverrideParentSurfaceProps
) {
  const parentSurface = useContext(SurfaceContext);
  const surface = getNextSurface(parentSurface, overrideParentSurfaceProps);
  const surfaceRef = useSurface<T>(surface);

  const surfaceContextValue = useMemo<SurfaceContextType>(
    () => surface,
    [surface]
  );

  return {
    surfaceContextValue,
    surfaceRef,
  };
}
