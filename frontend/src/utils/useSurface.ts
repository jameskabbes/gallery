import { useContext, useEffect, useRef, RefObject, useMemo } from 'react';
import { SurfaceContextValue } from '../types';
import { SurfaceContext } from '../contexts/Surface';

interface OverrideParentSurfaceProps {
  overrideMode?: SurfaceContextValue['mode'] | null;
  keepParentMode?: boolean;
}

function getNextSurface(
  surface: SurfaceContextValue,
  overrideParentSurfaceProps: OverrideParentSurfaceProps
): SurfaceContextValue {
  let mode: SurfaceContextValue['mode'];

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

function useSurface<T extends HTMLElement>(
  surface: SurfaceContextValue
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

function useSurfaceProvider<T extends HTMLElement>(
  overrideParentSurfaceProps: OverrideParentSurfaceProps
) {
  const parentSurface = useContext(SurfaceContext);
  const surface = getNextSurface(parentSurface, overrideParentSurfaceProps);
  const surfaceRef = useSurface<T>(surface);

  const surfaceContextValue = useMemo<SurfaceContextValue>(
    () => surface,
    [surface]
  );

  return {
    surfaceContextValue,
    surfaceRef,
  };
}

export {
  useSurface,
  useSurfaceProvider,
  getNextSurface,
  OverrideParentSurfaceProps,
};
