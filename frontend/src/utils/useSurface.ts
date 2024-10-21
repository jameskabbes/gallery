import { useEffect, useRef } from 'react';
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

function useSurface(
  surface: SurfaceContextValue
): React.RefObject<HTMLDivElement> {
  const ref = useRef<HTMLDivElement>(null);
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

export { useSurface, getNextSurface };
