import { useEffect, useRef } from 'react';

type SurfaceLevel = 'surface-even' | 'surface-odd';
const surfaceLevels: SurfaceLevel[] = ['surface-even', 'surface-odd'];

function useSurfaceLevel(
  overrideSurfaceLevel: SurfaceLevel | null
): React.RefObject<HTMLDivElement> {
  const ref = useRef(null);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    let surfaceLevel: SurfaceLevel = surfaceLevels[0];
    for (let level of surfaceLevels) {
      ref.current.classList.remove(level);
    }

    if (overrideSurfaceLevel) {
      surfaceLevel = overrideSurfaceLevel;
    } else {
      // proceed up the tree until we find a parent with surface-even or surface-odd

      let parent = element.parentElement;
      let inLoop = true;

      while (inLoop && parent) {
        for (let level of surfaceLevels) {
          if (parent.classList.contains(level)) {
            switch (level) {
              case 'surface-even': {
                surfaceLevel = 'surface-odd';
                inLoop = false;
                break;
              }
              case 'surface-odd': {
                surfaceLevel = 'surface-even';
                inLoop = false;
                break;
              }
            }
          }
        }
        parent = parent.parentElement;
      }
    }
    element.classList.add(surfaceLevel);
  }, []);

  return ref;
}

export { useSurfaceLevel, SurfaceLevel };
