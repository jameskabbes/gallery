import React, { useRef, useState } from 'react';
import { IoClose } from 'react-icons/io5';
import { useClickOutside } from '../../utils/useClickOutside';
import { CSSTransition } from 'react-transition-group';
import { useEscapeKey } from '../../contexts/EscapeKey';
import './Modal.css';

// change in modal.css when changing these values
const timeouts = {
  enter: 200,
  exit: 200,
};

interface Props {
  children: React.ReactNode;
  show: boolean;
  includeExit?: boolean;
  onExit?: () => void;
}

function Modal({
  children,
  show,
  includeExit = true,
  onExit = () => {},
}: Props) {
  const ref = useRef(null);

  useEscapeKey(onExit);
  useClickOutside(ref, onExit);

  return (
    <CSSTransition
      in={show}
      timeout={timeouts}
      classNames="modal"
      unmountOnExit
    >
      <div className="modal-overlay">
        <div className="modal-content" ref={ref}>
          {includeExit && (
            <div className="flex flex-row justify-end">
              <button>
                <p>
                  <IoClose onClick={onExit} className="cursor-pointer" />
                </p>
              </button>
            </div>
          )}
          {children}
        </div>
      </div>
    </CSSTransition>
  );
}

export { Modal };
