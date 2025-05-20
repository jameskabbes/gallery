import React, { createContext, useContext, useMemo } from 'react';
import { SurfaceContextType } from '../types';

export const SurfaceContext = createContext<SurfaceContextType>({
  level: -1,
  mode: 'b',
});
