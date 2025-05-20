import React, { useState, useEffect, useContext, useMemo } from 'react';
import { ModalsContext } from '../../contexts/Modals';
import { zIndex } from '../../config/constants';
import './Modal.css';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import { IoClose } from 'react-icons/io5';
import { Card1 } from '../Utils/Card';
import { useClickOutside } from '../../utils/useClickOutside';
import { useEscapeKey } from '../../contexts/EscapeKey';
import './Modal.css';

const timeouts = {
  enter: 200,
  exit: 200,
};

export function Modals() {
  const { activeModal, deleteModals } = useContext(ModalsContext);
  const {
    key = null,
    Component = null,
    componentProps = {},
    includeExitButton = true,
    contentAdditionalClassName = '',
    onExit = () => {},
  } = activeModal || {};

  const [ref, setRef] = useState<HTMLElement | null>(null);
  const refCallback = (node: HTMLElement | null) => {
    setRef(node);
  };

  function handleExit() {
    if (!!activeModal) {
      onExit();
      deleteModals([key]);
    }
  }

  useEscapeKey(() => handleExit());
  useClickOutside({ current: ref }, handleExit);

  return (
    <CSSTransition
      in={!!activeModal}
      timeout={timeouts}
      classNames="modal"
      unmountOnExit
    >
      <TransitionGroup
        className="fixed top-0 left-0 w-full h-full "
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          zIndex: zIndex.modalOverlay,
        }}
      >
        <CSSTransition
          in={!!activeModal}
          // if no children are provided, set key to null to trigger transition
          key={key}
          timeout={timeouts}
          classNames="modal"
        >
          <div className="absolute flex flex-col h-full w-full justify-center items-center p-2">
            {activeModal && (
              <Card1
                className={`overflow-y-auto ${contentAdditionalClassName}`}
                ref={refCallback}
              >
                {includeExitButton && (
                  <div className="flex flex-row justify-end">
                    <button onClick={handleExit}>
                      <IoClose />
                    </button>
                  </div>
                )}
                {Component && <Component {...componentProps} />}
              </Card1>
            )}
          </div>
        </CSSTransition>
      </TransitionGroup>
    </CSSTransition>
  );
}
