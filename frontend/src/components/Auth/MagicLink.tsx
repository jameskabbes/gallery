import React, { useState, useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  AuthModalType,
  ExtractResponseTypes,
  SendMagicLinkContextType,
} from '../../types';
import openapi_schema from '../../../../openapi_schema.json';

import { AuthContext } from '../../contexts/Auth';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { SendMagicLinkContext } from '../../contexts/SendMagicLink';

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
import { postRequestMagicLink } from '../../services/api/postRequestMagicLink';

function RequestMagicLink() {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const sendMagicLinkContext = useContext(SendMagicLinkContext);
  const authModalsContext = useContext(AuthModalsContext);
  const modalsContext = useContext(ModalsContext);

  const mediums: SendMagicLinkContextType['medium'][] = ['email', 'phone'];
  const modalKey: AuthModalType = 'requestMagicLink';

  useEffect(() => {
    if (sendMagicLinkContext.medium === 'email') {
      sendMagicLinkContext.setValid(
        sendMagicLinkContext.email.status === 'valid'
      );
    } else if (sendMagicLinkContext.medium === 'phone') {
      sendMagicLinkContext.setValid(
        sendMagicLinkContext.phoneNumber.status === 'valid'
      );
    }
  }, [
    sendMagicLinkContext.email.status,
    sendMagicLinkContext.phoneNumber.status,
    sendMagicLinkContext.medium,
  ]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    modalsContext.deleteModals([modalKey]);

    const toastId = toastContext.makePending({
      message: 'Sending Magic Link...',
    });

    const { status } = await postRequestMagicLink(authContext, {
      stay_signed_in: sendMagicLinkContext.staySignedIn.value,
      ...(sendMagicLinkContext.medium === 'email'
        ? { email: sendMagicLinkContext.email.value }
        : sendMagicLinkContext.medium === 'phone'
        ? { phone_number: sendMagicLinkContext.phoneNumber.value }
        : {}),
    });

    if (status === 200) {
      toastContext.update(toastId, {
        message: 'Magic Link Sent',
        type: 'success',
      });
    } else {
      toastContext.update(toastId, {
        message: 'Could not send magic link',
        type: 'error',
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
                onClick={() => sendMagicLinkContext.setMedium(medium)}
                className={`${
                  medium === sendMagicLinkContext.medium
                    ? ' border-primary-light dark:border-primary-dark'
                    : ''
                } hover:border-primary-light dark:hover:border-primary-dark flex-1`}
              >
                {medium}
              </Button2>
            ))}
          </div>

          <fieldset className="flex flex-col space-y-6">
            <section className="space-y-2">
              {sendMagicLinkContext.medium === 'email' ? (
                <>
                  <label htmlFor="email">Email</label>
                  <ValidatedInputString
                    state={sendMagicLinkContext.email}
                    setState={sendMagicLinkContext.setEmail}
                    id="login-with-email-email"
                    minLength={
                      openapi_schema.components.schemas.User.properties.email
                        .minLength
                    }
                    maxLength={
                      openapi_schema.components.schemas.User.properties.email
                        .maxLength
                    }
                    type="email"
                    checkValidity={true}
                    showStatus={true}
                    isValid={isEmailValid}
                  />
                </>
              ) : sendMagicLinkContext.medium === 'phone' ? (
                <>
                  <label htmlFor="phone">Phone Number</label>
                  <ValidatedInputPhoneNumber
                    state={sendMagicLinkContext.phoneNumber}
                    setState={sendMagicLinkContext.setPhoneNumber}
                    id="login-with-email-phone"
                    showStatus={true}
                  />
                </>
              ) : null}
            </section>
            <section className="flex flex-row items-center justify-center space-x-2">
              <ValidatedInputCheckbox
                state={sendMagicLinkContext.staySignedIn}
                setState={sendMagicLinkContext.setStaySignedIn}
                id="login-with-email-stay-signed-in"
              />
              <label htmlFor="login-with-email-stay-signed-in">
                Remember Me
              </label>
            </section>
          </fieldset>
          <span className="text-center mx-10">
            {`If an account with this ${
              sendMagicLinkContext.medium === 'email'
                ? 'email address'
                : sendMagicLinkContext.medium === 'phone'
                ? 'phone number'
                : null
            } exists, we will send you a magic login link.`}
          </span>
          <ButtonSubmit
            disabled={
              !sendMagicLinkContext.valid || sendMagicLinkContext.loading
            }
          >
            {sendMagicLinkContext.medium === 'email'
              ? 'Send Email'
              : sendMagicLinkContext.medium === 'phone'
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
  const access_token: string = searchParams.get('access_token');
  const stay_signed_in = searchParams.get('stay_signed_in') === 'True';
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
  }, [access_token, stay_signed_in]);

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
