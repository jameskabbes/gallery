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
import { ModalType } from '../types';

function useConfirmationModal() {
  const globalModalsContext = useContext(GlobalModalsContext);

  const defaultModalProps: Partial<ModalType> = {
    contentAdditionalStyle: { maxWidth: '400px', width: '100%' },
    modalKey: 'confirmation-modal',
  };

  function setModal(
    ModalComponent: React.ComponentType<any>,
    { onCancel = () => {}, onConfirm = () => {}, ...restModalProps }: any,
    modalProps: Partial<Omit<ModalType, 'children'>> = {}
  ) {
    globalModalsContext.setModal({
      children: (
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
    modalProps: Partial<Omit<ModalType, 'children'>> = {}
  ) {
    setModal(TextConfirmationModal, props, modalProps);
  }

  function checkButtonConfirmation(
    props: ButtonConfirmationModalProps,
    modalProps: Partial<Omit<ModalType, 'children'>> = {}
  ) {
    setModal(ButtonConfirmationModal, props, modalProps);
  }

  return {
    checkButtonConfirmation,
    checkTextConfirmation,
  };
}

export { useConfirmationModal };
