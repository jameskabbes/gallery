import React, { useContext } from 'react';
import { ModalsContext } from '../contexts/Modals';
import {
  ButtonConfirmationModalProps,
  ButtonConfirmationModal,
} from '../components/ConfirmationModals/ButtonConfirmationModal';
import {
  TextConfirmationModal,
  TextConfirmationModalProps,
} from '../components/ConfirmationModals/TextConfirmationModal';
import { ModalType } from '../types';

type ActivateModalFunction<T> = (
  modal: Omit<ModalType<T>, 'Component' | 'key' | 'componentProps'> &
    Partial<Pick<ModalType<T>, 'key'>> &
    Required<Pick<ModalType<T>, 'componentProps'>>
) => void;

export function useConfirmationModal() {
  const modalsContext = useContext(ModalsContext);

  const activateConfirmationModal: (modal: ModalType) => void = (modal) => {
    modalsContext.pushModals([
      {
        contentAdditionalClassName: 'max-w-[400px] w-full',
        ...modal,
      },
    ]);
  };

  const activateTextConfirmation: ActivateModalFunction<
    TextConfirmationModalProps
  > = ({ key = 'modal-confirmation-text', componentProps, ...modal }) => {
    const { onConfirm = () => {}, ...restComponentProps } = componentProps;

    activateConfirmationModal({
      key: key,
      Component: TextConfirmationModal,
      componentProps: {
        onConfirm: () => {
          onConfirm();
          modalsContext.deleteModals([key]);
        },
        ...restComponentProps,
      },
      ...modal,
    });
  };

  const activateButtonConfirmation: ActivateModalFunction<
    ButtonConfirmationModalProps
  > = ({ key = 'modal-confirmation-button', componentProps, ...modal }) => {
    const {
      onConfirm = () => {},
      onCancel = () => {},
      ...restComponentProps
    } = componentProps;

    activateConfirmationModal({
      key: key,
      Component: ButtonConfirmationModal,
      componentProps: {
        onConfirm: () => {
          onConfirm();
          modalsContext.deleteModals([key]);
        },
        onCancel: () => {
          onCancel();
          modalsContext.deleteModals([key]);
        },
        ...restComponentProps,
      },
      onExit: onCancel,
      ...modal,
    });
  };

  return {
    activateTextConfirmation,
    activateButtonConfirmation,
  };
}
