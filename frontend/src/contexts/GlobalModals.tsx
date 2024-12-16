import React, { useState, useReducer, createContext } from 'react';
import { GlobalModalsContextType } from '../types';

const GlobalModalsContext = createContext<GlobalModalsContextType>({
  modal: null,
  setModal: (modal) => {},
  updateModal: (modal) => {},
  clearModal: () => {},
});

function GlobalModalsContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [modal, setModal] = useState<GlobalModalsContextType['modal']>(null);

  const updateModal: GlobalModalsContextType['updateModal'] = (modal) => {
    setModal((prev) => ({ ...prev, ...modal }));
  };

  const clearModal: GlobalModalsContextType['clearModal'] = () => {
    setModal(null);
  };

  return (
    <GlobalModalsContext.Provider
      value={{
        modal,
        setModal,
        updateModal,
        clearModal,
      }}
    >
      {children}
    </GlobalModalsContext.Provider>
  );
}

export { GlobalModalsContext, GlobalModalsContextProvider };
