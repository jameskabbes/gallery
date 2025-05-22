import React from 'react';
import { paths, operations, components } from './openapi_schema';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { E164Number } from 'libphonenumber-js';

export type GetElementTypeFromArray<T extends any[]> = T extends (infer U)[]
  ? U
  : never;

export type FirstKey<T> = keyof {
  [K in keyof T as K extends string ? K : never]: T[K];
} extends infer O
  ? keyof O
  : never;

export interface CallApiOptions<TRequestData>
  extends AxiosRequestConfig<TRequestData> {
  url: AxiosRequestConfig<TRequestData>['url'];
  method: AxiosRequestConfig<TRequestData>['method'];
  authContext?: AuthContextType;
}

export interface UseApiCallReturn<T> extends AxiosResponse<T> {
  loading: boolean;
  refetch: () => void;
}

export type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

export interface ValidatedInputState<T> {
  value: T;
  status: 'valid' | 'invalid' | 'loading';
  error: string | null;
}

export const defaultValidatedInputState = <T>(
  defaultValue: T
): ValidatedInputState<T> => ({
  value: defaultValue,
  status: 'valid',
  error: null,
});

export interface DarkModeContextType {
  state: boolean;
  systemState: boolean;
  preference: 'light' | 'dark' | 'system';
  setPreference: (preference: 'light' | 'dark' | 'system') => void;
}

export type AuthModalType =
  | 'logIn'
  | 'requestSignUp'
  | 'requestMagicLink'
  | 'requestOTP'
  | 'verifyOTP';

export interface AuthModalsContextType {
  activate: (modal: AuthModalType | null) => void;
}

export interface LogInContextType {
  username: ValidatedInputState<string>;
  setUsername: React.Dispatch<
    React.SetStateAction<LogInContextType['username']>
  >;
  password: ValidatedInputState<string>;
  setPassword: React.Dispatch<
    React.SetStateAction<LogInContextType['password']>
  >;
  staySignedIn: ValidatedInputState<boolean>;
  setStaySignedIn: React.Dispatch<
    React.SetStateAction<LogInContextType['staySignedIn']>
  >;
  valid: boolean;
  setValid: React.Dispatch<React.SetStateAction<LogInContextType['valid']>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<LogInContextType['loading']>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<LogInContextType['error']>>;
}

export interface RequestSignUpContextType {
  email: ValidatedInputState<string>;
  setEmail: React.Dispatch<
    React.SetStateAction<RequestSignUpContextType['email']>
  >;
  valid: boolean;
  setValid: React.Dispatch<
    React.SetStateAction<RequestSignUpContextType['valid']>
  >;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<RequestSignUpContextType['loading']>
  >;
}

export interface RequestMagicLinkContextType {
  medium: 'email' | 'sms';
  setMedium: React.Dispatch<
    React.SetStateAction<RequestMagicLinkContextType['medium']>
  >;
  email: ValidatedInputState<string>;
  setEmail: React.Dispatch<
    React.SetStateAction<RequestMagicLinkContextType['email']>
  >;
  phoneNumber: ValidatedInputState<E164Number>;
  setPhoneNumber: React.Dispatch<
    React.SetStateAction<RequestMagicLinkContextType['phoneNumber']>
  >;
  valid: boolean;
  setValid: React.Dispatch<
    React.SetStateAction<RequestMagicLinkContextType['valid']>
  >;
  loading: boolean;
  setLoading: React.Dispatch<
    React.SetStateAction<RequestMagicLinkContextType['loading']>
  >;
}

export interface RequestOTPContextType {
  medium: 'email' | 'sms';
  setMedium: React.Dispatch<
    React.SetStateAction<RequestOTPContextType['medium']>
  >;
  email: ValidatedInputState<string>;
  setEmail: React.Dispatch<
    React.SetStateAction<RequestOTPContextType['email']>
  >;
  phoneNumber: ValidatedInputState<E164Number>;
  setPhoneNumber: React.Dispatch<
    React.SetStateAction<RequestOTPContextType['phoneNumber']>
  >;
  valid: boolean;
  setValid: React.Dispatch<
    React.SetStateAction<RequestOTPContextType['valid']>
  >;
}

export interface ModalType<T = Record<string, any>> {
  key: string;
  Component: React.ComponentType<any>;
  componentProps?: T;
  contentAdditionalClassName?: string;
  includeExitButton?: boolean;
  onExit?: () => void;
}

export type ModalUpdateType<T = Record<string, any>> = Partial<
  Omit<ModalType<Partial<T>>, 'key'>
> &
  Pick<ModalType<T>, 'key'>;

export interface ModalsContextType {
  activeModal: ModalType | null;
  pushModals: (modals: ModalType[]) => void;
  deleteModals: (modalKeys: ModalType['key'][]) => void;
  updateModals: (modals: ModalUpdateType[]) => void;
  upsertModals: (modals: ModalType[]) => void;
  swapActiveModal: (modal: ModalType) => void;
}

export interface DeviceContextType {
  isMobile: boolean;
}

export interface DataContextType {
  studios: null;
}

export type ToastId = string;

export interface ToastType {
  type: 'error' | 'info' | 'success' | 'pending';
  message: string;
}

export interface ToastNoType extends Omit<ToastType, 'type'> {}

export interface ToastContextState {
  toasts: Map<ToastId, ToastType>;
}

export interface ToastReducerActionTypes {
  ADD: {
    type: 'ADD';
    payload: {
      id: ToastId;
      toast: ToastType;
    };
  };
  REMOVE: {
    type: 'REMOVE';
    payload: string;
  };
  UPDATE: {
    type: 'UPDATE';
    payload: {
      id: ToastId;
      toast: Partial<ToastType>;
    };
  };
  CLEAR: {
    type: 'CLEAR';
  };
}

export type ToastReducerAction =
  ToastReducerActionTypes[keyof ToastReducerActionTypes];

export interface ToastContextType {
  state: ToastContextState;
  dispatch: React.Dispatch<ToastReducerAction>;
  make: (toast: ToastType) => ToastId;
  makePending: (toast: ToastNoType) => ToastId;
  update: (id: ToastId, toast: Partial<ToastType>) => void;
}

export type AuthContextState =
  components['schemas']['GetUserSessionInfoReturn'];

export interface AuthContextType {
  state: AuthContextState;
  setState: React.Dispatch<React.SetStateAction<AuthContextState>>;
  logOut: (toastId?: ToastId) => void;
  updateFromApiResponse: (data: any) => void;
}

export interface EscapeKeyContextType {
  addCallback: (callback: () => void) => void;
  removeCallback: (callback: () => void) => void;
}

export interface SurfaceContextType {
  level: number;
  mode: 'a' | 'b';
}

export type OrderByState = 'off' | 'asc' | 'desc';

interface HeaderKeys {
  auth_logout: string;
}

export interface SharedConfig {
  BACKEND_URL: string;
  FRONTEND_URL: string;
  AUTH_KEY: string;
  HEADER_KEYS: HeaderKeys;
  FRONTEND_ROUTES: Record<string, string>;
  SCOPE_NAME_MAPPING: Record<string, number>;
  VISIBILITY_LEVEL_NAME_MAPPING: Record<string, number>;
  PERMISSION_LEVEL_NAME_MAPPING: Record<string, number>;
  USER_ROLE_NAME_MAPPING: Record<string, number>;
  USER_ROLE_SCOPES: Record<string, string[]>;
  OTP_LENGTH: number;
  GOOGLE_CLIENT_ID: string;
}

interface ViteConfig {
  server: {
    port: number;
    host: boolean;
  };
}

export interface FrontendConfig {
  VITE: ViteConfig;
  OPENAPI_SCHEMA_PATH: string;
}

export interface Config {
  backendUrl: string;
  frontendUrl: string;
  authKey: string;
  headerKeys: HeaderKeys;
  frontendRoutes: Record<string, string>;
  scopeNameMapping: Record<string, number>;
  scopeIdMapping: Record<number, string>;
  visibilityLevelNameMapping: Record<string, number>;
  visibilityLevelIdMapping: Record<number, string>;
  permissionLevelNameMapping: Record<string, number>;
  permissionLevelIdMapping: Record<number, string>;
  userRoleNameMapping: Record<string, number>;
  userRoleIdMapping: Record<number, string>;
  userRoleScopes: Record<string, string[]>;
  otpLength: number;
  googleClientId: string;
  vite: ViteConfig;
  openapiSchemaPath: string;
}
