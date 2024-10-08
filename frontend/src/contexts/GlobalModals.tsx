import React, { useState, useReducer, createContext } from 'react';
import { GlobalModalsContext as GlobalModalsContextType } from '../types';

import { Modal } from '../types';

const defaultModal: Modal = {
  component: null,
  onExit: () => null,
  includeExitButton: true,
  contentStyle: {},
  key: null,
};

const GlobalModalsContext = createContext<GlobalModalsContextType>({
  activeModal: { ...defaultModal },
  setActiveModal: () => null,
});

interface Props {
  children: React.ReactNode;
}

function GlobalModalsContextProvider({ children }: Props) {
  const [activeModal, setActiveModal] = useState<
    GlobalModalsContextType['activeModal']
  >({ ...defaultModal });

  return (
    <GlobalModalsContext.Provider
      value={{
        activeModal,
        setActiveModal,
      }}
    >
      {children}
    </GlobalModalsContext.Provider>
  );
}

export { GlobalModalsContext, GlobalModalsContextProvider };
