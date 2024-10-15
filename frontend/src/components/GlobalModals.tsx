import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { Modals } from './Modal/Modals';

function GlobalModals() {
  const globalModalsContext = useContext(GlobalModalsContext);
  return <Modals activeModal={globalModalsContext.activeModal} />;
}

export { GlobalModals };
