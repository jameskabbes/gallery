import React, { useContext } from 'react';
import { LogIn } from './LogIn';
import { SignUp } from './SignUp';
import { LogInWithEmail } from './LogInWithEmail';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { Modals } from '../Modal/Modals';

function AuthModals() {
  const authModalsContext = useContext(AuthModalsContext);

  let component = null;
  switch (authModalsContext.activeModalType) {
    case 'logIn':
      component = <LogIn />;
      break;
    case 'signUp':
      component = <SignUp />;
      break;
    case 'logInWithEmail':
      component = <LogInWithEmail />;
      break;
  }

  return (
    <Modals
      activeModal={{
        component: component,
        onExit: () => {
          authModalsContext.setActiveModalType(null);
        },
        includeExitButton: true,
        className: 'max-w-[400px] w-full',
        contentStyle: {},
        key: authModalsContext.activeModalType || 'auth-modal',
      }}
    />
  );
}

export { AuthModals };
