import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { ConfirmationModal as ConfirmationModalType, Modal } from '../types';
import { ConfirmationModal } from '../components/ConfirmationModal';

function useConfirmationModal() {
  const globalModalsContext = useContext(GlobalModalsContext);

  const defaultContentStyle = { maxWidth: '400px', width: '100%' };

  function checkConfirmation(
    confirmationModalProps: ConfirmationModalType,
    modalProps: Partial<Omit<Modal, 'component'>> = {}
  ) {
    globalModalsContext.setModal({
      component: <ConfirmationModal {...confirmationModalProps} />,
      contentStyle: defaultContentStyle,
      ...modalProps,
    });
  }

  return {
    checkConfirmation,
  };
}

export { useConfirmationModal };
