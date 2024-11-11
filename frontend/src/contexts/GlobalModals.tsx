import React, { useState, useReducer, createContext } from 'react';
import { GlobalModalsContextType } from '../types';

import { Modal, defaultModal } from '../types';

const GlobalModalsContext = createContext<GlobalModalsContextType>({
  activeModal: { ...defaultModal },
  clearModal: () => null,
  setModal: (modal) => null,
});

interface Props {
  children: React.ReactNode;
}

function GlobalModalsContextProvider({ children }: Props) {
  const [activeModal, setActiveModal] = useState<
    GlobalModalsContextType['activeModal']
  >({ ...defaultModal });

  function clearModal() {
    setActiveModal({ ...defaultModal });
  }

  function setModal(modal: Partial<Modal>) {
    setActiveModal({
      ...defaultModal,
      onExit: clearModal,
      ...modal,
    });
  }

  return (
    <GlobalModalsContext.Provider
      value={{
        activeModal,
        clearModal,
        setModal,
      }}
    >
      {children}
    </GlobalModalsContext.Provider>
  );
}

export { GlobalModalsContext, GlobalModalsContextProvider };
