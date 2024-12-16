import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ModalType } from '../../types';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import { useEscapeKey } from '../../contexts/EscapeKey';
import { useClickOutside } from '../../utils/useClickOutside';
import { IoClose } from 'react-icons/io5';
import { Card1 } from '../Utils/Card';
import siteConfig from '../../../siteConfig.json';
import './Modal.css';

const timeouts = {
  enter: 200,
  exit: 200,
};

function Modal({
  contentAdditionalClassName = '',
  contentAdditionalStyle = {},
  overlayAdditionalClassName = '',
  overlayAdditionalStyle = {},
  includeExitButton = true,
  onExit = () => null,
  modalKey = 'modal-content',
  children,
}: ModalType) {
  const [ref, setRef] = useState<HTMLElement | null>(null);
  const refCallback = (node: HTMLElement | null) => {
    setRef(node);
  };
  useEscapeKey(() => onExit());
  useClickOutside({ current: ref }, () => onExit());

  return (
    <CSSTransition
      in={!!children}
      timeout={timeouts}
      classNames="modal"
      unmountOnExit
    >
      <TransitionGroup
        className={`fixed top-0 left-0 w-full h-full ${overlayAdditionalClassName}`}
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          zIndex: siteConfig.zIndex.modalOverlay,
          ...overlayAdditionalStyle,
        }}
      >
        <CSSTransition
          in={!!children}
          // if no children are provided, set key to null to trigger transition
          key={!!children ? modalKey : null}
          timeout={timeouts}
          classNames="modal"
        >
          <div className="absolute h-full w-full flex flex-col justify-center items-center p-2">
            {children && (
              <Card1
                style={{
                  ...contentAdditionalStyle,
                }}
                ref={refCallback}
                className={`overflow-y-auto ${contentAdditionalClassName}`}
              >
                {includeExitButton && (
                  <div className="flex flex-row justify-end">
                    <button onClick={() => onExit()}>
                      <IoClose />
                    </button>
                  </div>
                )}
                {children}
              </Card1>
            )}
          </div>
        </CSSTransition>
      </TransitionGroup>
    </CSSTransition>
  );
}

export { Modal };
