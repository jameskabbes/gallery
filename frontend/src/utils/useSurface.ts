import { useEffect, useRef } from 'react';
import { SurfaceContextValue } from '../types';
import { useSurfaceContext } from '../contexts/Surface';

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

export { useSurface };
