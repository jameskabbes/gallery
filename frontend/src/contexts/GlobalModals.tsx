import React, { useState, useReducer, createContext } from 'react';
import { GlobalModalsContext as GlobalModalsContextType } from '../types';

import { Modal, defaultModal } from '../types';

const GlobalModalsContext = createContext<GlobalModalsContextType>({
  activeModal: { ...defaultModal },
  setModal: (modal) => null,
});

interface Props {
  children: React.ReactNode;
}

function GlobalModalsContextProvider({ children }: Props) {
  const [activeModal, setActiveModal] = useState<
    GlobalModalsContextType['activeModal']
  >({ ...defaultModal });

  function setModal(modal: Partial<Modal>) {
    setActiveModal({
      ...defaultModal,
      onExit: () => setActiveModal({ ...defaultModal }),
      ...modal,
    });
  }

  return (
    <GlobalModalsContext.Provider
      value={{
        activeModal,
        setModal,
      }}
    >
      {children}
    </GlobalModalsContext.Provider>
  );
}

export { GlobalModalsContext, GlobalModalsContextProvider };
