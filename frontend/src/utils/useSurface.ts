import { useContext, useEffect, useRef, RefObject, useMemo } from 'react';
import { SurfaceContextValue } from '../types';
import { SurfaceContext } from '../contexts/Surface';

function getNextSurface(
  surface: SurfaceContextValue,
  overrideMode: SurfaceContextValue['mode']
): SurfaceContextValue {
  return {
    level: surface.level + 1,
    mode: overrideMode ? overrideMode : surface.mode === 'a' ? 'b' : 'a',
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

interface UseSurfaceProviderProps {
  overrideMode?: SurfaceContextValue['mode'] | null;
}

function useSurfaceProvider<T extends HTMLElement>({
  overrideMode = null,
}: UseSurfaceProviderProps) {
  const parentSurface = useContext(SurfaceContext);
  const surface = getNextSurface(parentSurface, overrideMode);
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
  UseSurfaceProviderProps,
};
