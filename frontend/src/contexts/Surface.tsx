import React, { createContext, useContext, useMemo } from 'react';
import { SurfaceContextValue } from '../types';

const SurfaceContext = createContext<SurfaceContextValue>({
  level: -1,
  mode: 'b',
});

function useSurfaceContext() {
  return useContext(SurfaceContext);
}

export { SurfaceContext, useSurfaceContext };
