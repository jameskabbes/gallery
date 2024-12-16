import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { Modal } from './Modal/Modal';
import siteConfig from '../../siteConfig.json';

function GlobalModals() {
  const globalModalsContext = useContext(GlobalModalsContext);
  return (
    <Modal
      overlayAdditionalStyle={{ zIndex: siteConfig.zIndex.globalModalOverlay }}
      onExit={globalModalsContext.clearModal}
      {...globalModalsContext.modal}
    />
  );
}

export { GlobalModals };
