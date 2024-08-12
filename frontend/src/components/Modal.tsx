import React, { useContext } from 'react';
import { IoClose } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';

import { ModalsContext } from '../contexts/Modals';

interface Props {
  children: React.ReactNode;
  includeExit?: boolean;
}

function Modal({ children, includeExit = true }: Props) {
  const modalsContext = useContext(ModalsContext);

  return (
    <div className="card">
      {includeExit && (
        <p className="flex flex-row justify-end">
          <IoClose
            onClick={() => modalsContext.dispatch({ type: 'POP' })}
            className="cursor-pointer"
          />
        </p>
      )}
      {children}
    </div>
  );
}

export { Modal };
