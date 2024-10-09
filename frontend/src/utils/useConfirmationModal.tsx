import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { ConfirmationModal as ConfirmationModalType } from '../types';
import { ConfirmationModal } from '../components/ConfirmationModal';

function useConfirmationModal() {
  const globalModalsContext = useContext(GlobalModalsContext);

  function checkConfirmation(modalProps: ConfirmationModalType) {
    globalModalsContext.setModal({
      component: <ConfirmationModal {...modalProps} />,
      key: 'confirmation-modal',
    });
  }

  return {
    checkConfirmation,
  };
}

export { useConfirmationModal };
