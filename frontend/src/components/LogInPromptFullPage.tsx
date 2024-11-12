import React, { useContext } from 'react';
import { AuthModalsContext } from '../contexts/AuthModals';
import { Button1 } from './Utils/Button';

function LogInPromptFullPage() {
  const authModalsContext = useContext(AuthModalsContext);

  return (
    <div className="flex-1 flex flex-col justify-center">
      <div className="flex flex-row justify-center">
        <Button1 onClick={() => authModalsContext.setActiveModalType('logIn')}>
          Log In
        </Button1>
      </div>
    </div>
  );
}

export { LogInPromptFullPage };
