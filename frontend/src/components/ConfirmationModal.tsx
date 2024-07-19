import React, { useContext } from 'react';
import { ConfirmationModalContext } from '../contexts/ConfirmationModal';

function ConfirmationModal(): JSX.Element {
  let context = useContext(ConfirmationModalContext);

  if (context.state.isActive) {
    return (
      <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center">
        <div className="p-4 card">
          <h4>{context.state.title}</h4>
          <p>{context.state.message}</p>
          <div className="flex flex-row justify-center space-x-2">
            <button onClick={() => context.dispatch({ type: 'CANCEL' })}>
              Cancel
            </button>
            <button onClick={() => context.dispatch({ type: 'CONFIRM' })}>
              Confirm
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export { ConfirmationModal };
