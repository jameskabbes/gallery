import React, { useContext, useEffect } from 'react';
import { AuthModalsContext } from '../contexts/AuthModals';
import { AuthContext } from '../contexts/Auth';
import { Button1 } from '../components/Utils/Button';

function LogIn() {
  const authModalsContext = useContext(AuthModalsContext);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    if (!authContext.state.user) {
      authModalsContext.activate('logIn');
    }
  }, [authContext.state.user]);

  if (!authContext.state.user) {
    return (
      <div className="flex-1 flex flex-col justify-center">
        <div className="flex flex-row justify-center">
          <Button1 onClick={() => authModalsContext.activate('logIn')}>
            Log In
          </Button1>
        </div>
      </div>
    );
  }
}

export { LogIn };
