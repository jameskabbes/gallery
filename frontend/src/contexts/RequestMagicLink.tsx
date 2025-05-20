import React, { useEffect, useState, useReducer, createContext } from 'react';
import {
  RequestMagicLinkContextType,
  defaultValidatedInputState,
} from '../types';

export const RequestMagicLinkContext =
  createContext<RequestMagicLinkContextType>({
    medium: null,
    setMedium: () => {},
    email: null,
    setEmail: () => {},
    phoneNumber: null,
    setPhoneNumber: () => {},
    valid: false,
    setValid: () => {},
    loading: false,
    setLoading: () => {},
  });

export function RequestMagicLinkContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [medium, setMedium] =
    useState<RequestMagicLinkContextType['medium']>('email');
  const [email, setEmail] = useState<RequestMagicLinkContextType['email']>({
    ...defaultValidatedInputState<
      RequestMagicLinkContextType['email']['value']
    >(''),
  });
  const [phoneNumber, setPhoneNumber] = useState<
    RequestMagicLinkContextType['phoneNumber']
  >({
    ...defaultValidatedInputState<
      RequestMagicLinkContextType['phoneNumber']['value']
    >(null),
  });
  const [valid, setValid] =
    useState<RequestMagicLinkContextType['valid']>(false);
  const [loading, setLoading] =
    useState<RequestMagicLinkContextType['loading']>(false);

  return (
    <RequestMagicLinkContext.Provider
      value={{
        medium,
        setMedium,
        email,
        setEmail,
        phoneNumber,
        setPhoneNumber,
        valid,
        setValid,
        loading,
        setLoading,
      }}
    >
      {children}
    </RequestMagicLinkContext.Provider>
  );
}
