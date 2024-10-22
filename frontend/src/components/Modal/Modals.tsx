import React, { useRef } from 'react';
import { Modal } from '../../types';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import './Modal.css';
import { useEscapeKey } from '../../contexts/EscapeKey';
import { useClickOutside } from '../../utils/useClickOutside';
import { IoClose } from 'react-icons/io5';
import { Card1 } from '../Utils/Card';

const timeouts = {
  enter: 200,
  exit: 200,
};

interface Props {
  activeModal: Modal | null;
  overlayStyle?: React.CSSProperties;
}

function Modals({ activeModal, overlayStyle = {} }: Props) {
  const ref = useRef(null);

  useEscapeKey(() => activeModal.onExit());
  useClickOutside(ref, () => activeModal.onExit());

  return (
    <CSSTransition
      in={activeModal.component !== null}
      timeout={timeouts}
      classNames="modal"
      unmountOnExit
    >
      <TransitionGroup className="modal-overlay relative" style={overlayStyle}>
        <CSSTransition
          in={activeModal.component !== null}
          key={activeModal.key || 'modal-content'}
          timeout={timeouts}
          classNames="modal"
        >
          <>
            {activeModal.component !== null && (
              <div className="absolute h-full w-full flex flex-col justify-center items-center p-2">
                <Card1 ref={ref} style={activeModal.contentStyle} className="">
                  {activeModal.includeExitButton && (
                    <div className="flex flex-row justify-end">
                      <button>
                        <p>
                          <IoClose
                            onClick={() => activeModal.onExit()}
                            className="cursor-pointer"
                          />
                        </p>
                      </button>
                    </div>
                  )}
                  {activeModal.component}
                </Card1>
              </div>
            )}
          </>
        </CSSTransition>
      </TransitionGroup>
    </CSSTransition>
  );
}

export { Modals };
