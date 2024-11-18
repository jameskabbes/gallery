import React, { useContext } from 'react';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import {
  ButtonConfirmationModalProps,
  ButtonConfirmationModal,
} from '../components/ConfirmationModals/ButtonConfirmationModal';
import {
  TextConfirmationModal,
  TextConfirmationModalProps,
} from '../components/ConfirmationModals/TextConfirmationModal';
import { Modal } from '../types';

function useConfirmationModal() {
  const globalModalsContext = useContext(GlobalModalsContext);

  const defaultModalProps: Partial<Modal> = {
    contentStyle: { maxWidth: '400px', width: '100%' },
    key: 'confirmation-modal',
  };

  function setModal(
    ModalComponent: React.ComponentType<any>,
    { onCancel = () => {}, onConfirm = () => {}, ...restModalProps }: any,
    modalProps: Partial<Omit<Modal, 'component'>> = {}
  ) {
    globalModalsContext.setModal({
      component: (
        <ModalComponent
          {...{
            onCancel: () => {
              onCancel();
              globalModalsContext.clearModal();
            },
            onConfirm: () => {
              onConfirm();
              globalModalsContext.clearModal();
            },
            ...restModalProps,
          }}
        />
      ),
      ...defaultModalProps,
      ...modalProps,
    });
  }

  function checkTextConfirmation(
    props: TextConfirmationModalProps,
    modalProps: Partial<Omit<Modal, 'component'>> = {}
  ) {
    setModal(TextConfirmationModal, props, modalProps);
  }

  function checkButtonConfirmation(
    props: ButtonConfirmationModalProps,
    modalProps: Partial<Omit<Modal, 'component'>> = {}
  ) {
    setModal(ButtonConfirmationModal, props, modalProps);
  }

  return {
    checkButtonConfirmation,
    checkTextConfirmation,
  };
}

export { useConfirmationModal };
