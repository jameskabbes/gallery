import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { ConfirmationModal as ConfirmationModalType, Modal } from '../types';
import { ConfirmationModal } from '../components/ConfirmationModal';

function useConfirmationModal() {
  const globalModalsContext = useContext(GlobalModalsContext);

  const defaultModalProps: Partial<Modal> = {
    contentStyle: { maxWidth: '400px', width: '100%' },
    key: 'confirmation-modal',
  };

  function checkConfirmation(
    {
      onCancel = () => {},
      onConfirm = () => {},
      ...restConfirmationModalProps
    }: ConfirmationModalType,
    modalProps: Partial<Omit<Modal, 'component'>> = {}
  ) {
    globalModalsContext.setModal({
      component: (
        <ConfirmationModal
          {...{
            onCancel: () => {
              onCancel();
              globalModalsContext.clearModal();
            },
            onConfirm: () => {
              onConfirm();
              globalModalsContext.clearModal();
            },
            ...restConfirmationModalProps,
          }}
        />
      ),
      ...defaultModalProps,
      ...modalProps,
    });
  }

  return {
    checkConfirmation,
  };
}

export { useConfirmationModal };
