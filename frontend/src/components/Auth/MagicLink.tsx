import React, { useState, useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthModalType,
  ExtractResponseTypes,
  RequestMagicLinkContextType,
} from '../../types';
import openapi_schema from '../../../../openapi_schema.json';

import { AuthContext } from '../../contexts/Auth';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { RequestMagicLinkContext } from '../../contexts/RequestMagicLink';

import { isEmailValid } from '../../services/isEmailValid';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { Button2, ButtonSubmit } from '../Utils/Button';
import { ValidatedInputCheckbox } from '../Form/ValidatedInputCheckbox';
import { ModalsContext } from '../../contexts/Modals';
import { ValidatedInputPhoneNumber } from '../Form/ValidatedInputPhoneNumber';
import { ToastContext } from '../../contexts/Toast';

import { useLocation } from 'react-router-dom';
import { Loader1 } from '../Utils/Loader';
import { IoWarning } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';
import { postRequestMagicLinkEmail } from '../../services/api/postRequestMagicLinkEmail';
import { postRequestMagicLinkSMS } from '../../services/api/postRequestMagicLinkSMS';

function RequestMagicLink() {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const requestMagicLinkContext = useContext(RequestMagicLinkContext);
  const authModalsContext = useContext(AuthModalsContext);
  const modalsContext = useContext(ModalsContext);

  const mediums: RequestMagicLinkContextType['medium'][] = ['email', 'sms'];
  const modalKey: AuthModalType = 'requestMagicLink';

  useEffect(() => {
    if (requestMagicLinkContext.medium === 'email') {
      requestMagicLinkContext.setValid(
        requestMagicLinkContext.email.status === 'valid'
      );
    } else if (requestMagicLinkContext.medium === 'sms') {
      requestMagicLinkContext.setValid(
        requestMagicLinkContext.phoneNumber.status === 'valid'
      );
    }
  }, [
    requestMagicLinkContext.email.status,
    requestMagicLinkContext.phoneNumber.status,
    requestMagicLinkContext.medium,
  ]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    authModalsContext.activate(null);

    if (requestMagicLinkContext.medium === 'email') {
      var { status } = await postRequestMagicLinkEmail(authContext, {
        email: requestMagicLinkContext.email.value,
      });
    } else if (requestMagicLinkContext.medium === 'sms') {
      var { status } = await postRequestMagicLinkSMS(authContext, {
        phone_number: requestMagicLinkContext.phoneNumber.value,
      });
    }
  }
  return (
    <div id="login-with-email" className="flex flex-col">
      <div className="flex flex-col">
        <form onSubmit={handleSubmit} className="flex flex-col space-y-6">
          <header>Send Magic Link</header>
          <div className="flex flex-row space-x-2">
            {mediums.map((medium) => (
              <Button2
                type="button"
                key={medium}
                onClick={() => requestMagicLinkContext.setMedium(medium)}
                isActive={medium === requestMagicLinkContext.medium}
                className="flex-1"
              >
                {medium}
              </Button2>
            ))}
          </div>

          <fieldset className="flex flex-col space-y-6">
            <section className="space-y-2">
              {requestMagicLinkContext.medium === 'email' ? (
                <>
                  <label htmlFor="request-magic-link-email">Email</label>
                  <ValidatedInputString
                    state={requestMagicLinkContext.email}
                    setState={requestMagicLinkContext.setEmail}
                    id="request-magic-link-email"
                    minLength={
                      openapi_schema.components.schemas
                        .PostRequestMagicLinkEmailRequest.properties.email
                        .minLength
                    }
                    maxLength={
                      openapi_schema.components.schemas
                        .PostRequestMagicLinkEmailRequest.properties.email
                        .maxLength
                    }
                    type="email"
                    checkValidity={true}
                    showStatus={true}
                    isValid={isEmailValid}
                  />
                </>
              ) : requestMagicLinkContext.medium === 'sms' ? (
                <>
                  <label htmlFor="request-magic-link-phone-number">
                    Phone Number
                  </label>
                  <ValidatedInputPhoneNumber
                    state={requestMagicLinkContext.phoneNumber}
                    setState={requestMagicLinkContext.setPhoneNumber}
                    id="request-magic-link-phone-number"
                    showStatus={true}
                  />
                </>
              ) : null}
            </section>
          </fieldset>
          <span className="text-center mx-10">
            {`If an account with this ${
              requestMagicLinkContext.medium === 'email'
                ? 'email address'
                : requestMagicLinkContext.medium === 'sms'
                ? 'phone number'
                : null
            } exists, we will send you a magic login link.`}
          </span>
          <ButtonSubmit
            disabled={
              !requestMagicLinkContext.valid || requestMagicLinkContext.loading
            }
          >
            {requestMagicLinkContext.medium === 'email'
              ? 'Send Email'
              : requestMagicLinkContext.medium === 'sms'
              ? 'Send SMS'
              : null}
          </ButtonSubmit>
        </form>
        <h6
          className="cursor-pointer underline text-center mt-2"
          onClick={() => {
            authModalsContext.activate('logIn');
          }}
        >
          Back to Login
        </h6>
      </div>
    </div>
  );
}

function VerifyMagicLink() {
  const location = useLocation();
  const authContext = useContext(AuthContext);
  const searchParams = new URLSearchParams(location.search);
  const [status, setStatus] = useState<number>(null);
  const token: string = searchParams.get('token');
  const modalsContext = useContext(ModalsContext);
  const modalKey = 'modal-verify-magic-link';

  useEffect(() => {
    // async function verifyMagicLink() {
    //   setStatus(null);
    //   const { status } = await postRequestMagicLink(authContext, {
    //     access_token: access_token,
    //   });
    //   setStatus(status);
    // }
    // verifyMagicLink();
  }, [token]);

  function Component({ status }: { status: number }) {
    return (
      <div className="flex flex-col items-center space-y-2">
        <h1>
          {status === null ? (
            <Loader1 />
          ) : status === 200 ? (
            <IoCheckmark className="text-green-500" />
          ) : (
            <IoWarning className="text-red-500" />
          )}
        </h1>
        <h4 className="text-center">
          {status === null
            ? 'Verifying your magic link'
            : status === 200
            ? 'Magic link verified. You can close this tab'
            : 'Could not verify magic link'}
        </h4>
      </div>
    );
  }

  useEffect(() => {
    modalsContext.upsertModals([
      {
        Component: Component,
        key: modalKey,
        contentAdditionalClassName: 'max-w-[400px] w-full',
        componentProps: { status },
      },
    ]);
  }, [status]);

  return null;
}

export { RequestMagicLink, VerifyMagicLink };
