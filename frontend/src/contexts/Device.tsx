import React, { useEffect, useState, createContext } from 'react';
import { DeviceContextType } from '../types';

export const DeviceContext = createContext<DeviceContextType>({
  isMobile: false,
});

export function DeviceContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mobileMediaQuery = window.matchMedia('(max-width: 767px)');
    setIsMobile(mobileMediaQuery.matches);

    const handleDeviceChange = (e: MediaQueryListEvent) => {
      setIsMobile(e.matches);
    };

    mobileMediaQuery.addEventListener('change', handleDeviceChange);
    return () => {
      mobileMediaQuery.removeEventListener('change', handleDeviceChange);
    };
  }, []);

  return (
    <DeviceContext.Provider value={{ isMobile }}>
      {children}
    </DeviceContext.Provider>
  );
}
