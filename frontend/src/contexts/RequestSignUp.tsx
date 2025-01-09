import React, { useEffect, useState, useReducer, createContext } from 'react';
import { RequestSignUpContextType, defaultValidatedInputState } from '../types';

const RequestSignUpContext = createContext<RequestSignUpContextType>({
  email: null,
  setEmail: () => {},
  staySignedIn: null,
  setStaySignedIn: () => {},
  valid: false,
  setValid: () => {},
  loading: false,
  setLoading: () => {},
});

function RequestSignUpContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [email, setEmail] = useState<RequestSignUpContextType['email']>({
    ...defaultValidatedInputState<RequestSignUpContextType['email']['value']>(
      ''
    ),
  });
  const [staySignedIn, setStaySignedIn] = useState<
    RequestSignUpContextType['staySignedIn']
  >({
    ...defaultValidatedInputState<
      RequestSignUpContextType['staySignedIn']['value']
    >(true),
  });

  const [valid, setValid] = useState<RequestSignUpContextType['valid']>(false);
  const [loading, setLoading] =
    useState<RequestSignUpContextType['loading']>(false);

  return (
    <RequestSignUpContext.Provider
      value={{
        email,
        setEmail,
        staySignedIn,
        setStaySignedIn,
        valid,
        setValid,
        loading,
        setLoading,
      }}
    >
      {children}
    </RequestSignUpContext.Provider>
  );
}

export { RequestSignUpContext, RequestSignUpContextProvider };
