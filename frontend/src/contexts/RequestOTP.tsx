import React, { createContext, useState } from 'react';

import { RequestOTPContextType, defaultValidatedInputState } from '../types';

export const RequestOTPContext = createContext<RequestOTPContextType>({
  medium: null,
  setMedium: () => {},
  email: null,
  setEmail: () => {},
  phoneNumber: null,
  setPhoneNumber: () => {},
  valid: false,
  setValid: () => {},
});

interface Props {
  children: React.ReactNode;
}

export function RequestOTPContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [medium, setMedium] =
    useState<RequestOTPContextType['medium']>('email');
  const [email, setEmail] = useState<RequestOTPContextType['email']>({
    ...defaultValidatedInputState<RequestOTPContextType['email']['value']>(''),
  });
  const [phoneNumber, setPhoneNumber] = useState<
    RequestOTPContextType['phoneNumber']
  >({
    ...defaultValidatedInputState<
      RequestOTPContextType['phoneNumber']['value']
    >(null),
  });
  const [valid, setValid] = useState<RequestOTPContextType['valid']>(false);

  return (
    <RequestOTPContext.Provider
      value={{
        medium,
        setMedium,
        email,
        setEmail,
        phoneNumber,
        setPhoneNumber,
        valid,
        setValid,
      }}
    >
      {children}
    </RequestOTPContext.Provider>
  );
}
