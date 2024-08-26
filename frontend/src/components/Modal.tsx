import React, { useRef } from 'react';
import { IoClose } from 'react-icons/io5';

import { useEscapeKey } from '../utils/useEscapeKey';
import { useClickOutside } from '../utils/useClickOutside';

interface Props {
  children: React.ReactNode;
  includeExit?: boolean;
  onExit?: () => void;
}

function Modal({ children, includeExit = true, onExit = () => {} }: Props) {
  let ref = useRef(null);

  useEscapeKey(onExit);
  useClickOutside(ref, onExit);

  return (
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
  );
}

export { Modal };
