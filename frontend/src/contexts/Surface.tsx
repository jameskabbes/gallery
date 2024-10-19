import React, { createContext, useContext, useMemo } from 'react';
import { SurfaceContextValue } from '../types';

const SurfaceContext = createContext<SurfaceContextValue>({
  level: 0,
  mode: 'even',
});

function useSurfaceContext() {
  return useContext(SurfaceContext);
}

export { SurfaceContext, useSurfaceContext };
