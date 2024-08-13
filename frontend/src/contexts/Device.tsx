import React, { useEffect, useState, createContext } from 'react';
import { DeviceContext as DeviceContextType } from '../types';

const DeviceContext = createContext<DeviceContextType>({ isMobile: false });

interface Props {
  children: React.ReactNode;
}

function DeviceContextProvider({ children }: Props) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mobileMediaQuery = window.matchMedia('(max-width: 768px)');
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

export { DeviceContext, DeviceContextProvider };
