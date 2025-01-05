import React, { useEffect, useState, useReducer, createContext } from 'react';
import { SendMagicLinkContextType, defaultValidatedInputState } from '../types';

const SendMagicLinkContext = createContext<SendMagicLinkContextType>({
  medium: null,
  setMedium: () => {},
  email: null,
  setEmail: () => {},
  phoneNumber: null,
  setPhoneNumber: () => {},
  staySignedIn: null,
  setStaySignedIn: () => {},
  valid: false,
  setValid: () => {},
  loading: false,
  setLoading: () => {},
});

interface Props {
  children: React.ReactNode;
}

function SendMagicLinkContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [medium, setMedium] =
    useState<SendMagicLinkContextType['medium']>('email');
  const [email, setEmail] = useState<SendMagicLinkContextType['email']>({
    ...defaultValidatedInputState<SendMagicLinkContextType['email']['value']>(
      ''
    ),
  });
  const [phoneNumber, setPhoneNumber] = useState<
    SendMagicLinkContextType['phoneNumber']
  >({
    ...defaultValidatedInputState<
      SendMagicLinkContextType['phoneNumber']['value']
    >(null),
  });
  const [staySignedIn, setStaySignedIn] = useState<
    SendMagicLinkContextType['staySignedIn']
  >({
    ...defaultValidatedInputState<
      SendMagicLinkContextType['staySignedIn']['value']
    >(true),
  });

  const [valid, setValid] = useState<SendMagicLinkContextType['valid']>(false);
  const [loading, setLoading] =
    useState<SendMagicLinkContextType['loading']>(false);

  return (
    <SendMagicLinkContext.Provider
      value={{
        medium,
        setMedium,
        email,
        setEmail,
        phoneNumber,
        setPhoneNumber,
        staySignedIn,
        setStaySignedIn,
        valid,
        setValid,
        loading,
        setLoading,
      }}
    >
      {children}
    </SendMagicLinkContext.Provider>
  );
}

export { SendMagicLinkContext, SendMagicLinkContextProvider };
