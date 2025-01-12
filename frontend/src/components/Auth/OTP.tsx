import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../../contexts/Auth';
import { RequestOTPContext } from '../../contexts/RequestOTP';
import { AuthModalsContext } from '../../contexts/AuthModals';
import {
  AuthModalType,
  defaultValidatedInputState,
  RequestOTPContextType,
  ValidatedInputState,
} from '../../types';
import { postRequestOTPEmail } from '../../services/api/postRequestOTPEmail';
import { postRequestOTPSMS } from '../../services/api/postRequestOTPSMS';
import { postLogInOTPEmail } from '../../services/api/postLogInOTPEmail';
import { Button2, ButtonSubmit } from '../Utils/Button';
import openapi_schema from '../../../../openapi_schema.json';
import { isEmailValid } from '../../services/isEmailValid';
import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ValidatedInputPhoneNumber } from '../Form/ValidatedInputPhoneNumber';
import { postLogInOTPPhoneNumber } from '../../services/api/postLogInOTPPhoneNumber';

function RequestOTP() {
  const authContext = useContext(AuthContext);
  const requestOTPContext = useContext(RequestOTPContext);
  const authModalsContext = useContext(AuthModalsContext);

  const mediums: RequestOTPContextType['medium'][] = ['email', 'sms'];

  useEffect(() => {
    if (requestOTPContext.medium === 'email') {
      requestOTPContext.setValid(requestOTPContext.email.status === 'valid');
    } else if (requestOTPContext.medium === 'sms') {
      requestOTPContext.setValid(
        requestOTPContext.phoneNumber.status === 'valid'
      );
    }
  }, [
    requestOTPContext.email.status,
    requestOTPContext.phoneNumber.status,
    requestOTPContext.medium,
  ]);

  async function handleSubmitRequest(e: React.FormEvent) {
    e.preventDefault();
    authModalsContext.activate('verifyOTP');

    if (requestOTPContext.medium === 'email') {
      var { status } = await postRequestOTPEmail(authContext, {
        email: requestOTPContext.email.value,
      });
    } else if (requestOTPContext.medium === 'sms') {
      var { status } = await postRequestOTPSMS(authContext, {
        phone_number: requestOTPContext.phoneNumber.value,
      });
    }
  }

  return (
    <div id="otp" className="flex flex-col">
      <form onSubmit={handleSubmitRequest} className="flex flex-col space-y-6">
        <header>Send Code</header>
        <div className="flex flex-row space-x-2">
          {mediums.map((medium) => (
            <Button2
              type="button"
              key={medium}
              isActive={requestOTPContext.medium === medium}
              onClick={() => requestOTPContext.setMedium(medium)}
              className="flex-1"
            >
              {medium}
            </Button2>
          ))}
        </div>
        <fieldset className="flex flex-col space-y-6">
          <section className="space-y-2">
            {requestOTPContext.medium === 'email' ? (
              <>
                <label htmlFor="email">Email</label>
                <ValidatedInputString
                  state={requestOTPContext.email}
                  setState={requestOTPContext.setEmail}
                  id="request-otp-email"
                  minLength={
                    openapi_schema.components.schemas
                      .PostLoginWithOTPEmailRequest.properties.email.minLength
                  }
                  maxLength={
                    openapi_schema.components.schemas
                      .PostLoginWithOTPEmailRequest.properties.email.maxLength
                  }
                  type="email"
                  checkValidity={true}
                  showStatus={true}
                  isValid={isEmailValid}
                />
              </>
            ) : requestOTPContext.medium === 'sms' ? (
              <>
                <label htmlFor="phone">Phone Number</label>
                <ValidatedInputPhoneNumber
                  state={requestOTPContext.phoneNumber}
                  setState={requestOTPContext.setPhoneNumber}
                  id="request-otp-phone-number"
                  showStatus={true}
                />
              </>
            ) : null}
          </section>
        </fieldset>
        <span className="text-center mx-10">
          {`If an account with this ${
            requestOTPContext.medium === 'email'
              ? 'email address'
              : requestOTPContext.medium === 'sms'
              ? 'phone number'
              : null
          } exists, we will send you a code.`}
        </span>
        <ButtonSubmit disabled={!requestOTPContext.valid}>
          {requestOTPContext.medium === 'email'
            ? 'Send Email'
            : requestOTPContext.medium === 'sms'
            ? 'Send SMS'
            : null}
        </ButtonSubmit>
      </form>
    </div>
  );
}

function VerifyOTP() {
  const authModalsContext = useContext(AuthModalsContext);
  const authContext = useContext(AuthContext);
  const requestOTPContext = useContext(RequestOTPContext);

  const [code, setCode] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });
  const [valid, setValid] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setValid(code.status === 'valid');
  }, [code.status]);

  async function handleSubmitVerify(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    if (requestOTPContext.medium === 'email') {
      var { data, status } = await postLogInOTPEmail(authContext, {
        code: code.value,
        email: requestOTPContext.email.value,
      });
    } else if (requestOTPContext.medium === 'sms') {
      var { data, status } = await postLogInOTPPhoneNumber(authContext, {
        code: code.value,
        phone_number: requestOTPContext.phoneNumber.value,
      });
    }
    setLoading(false);
    console.log(data);
    console.log(status);

    if (status === 200) {
      authModalsContext.activate(null);
      authContext.updateFromApiResponse(data);
    }
  }

  return (
    <form onSubmit={handleSubmitVerify} className="flex flex-col space-y-6">
      <header>Enter Code</header>
      <p
        className="underline text-center cursor-pointer"
        onClick={() => authModalsContext.activate('requestOTP')}
      >
        Need a new code?
      </p>
      <fieldset>
        <ValidatedInputString
          state={code}
          setState={setCode}
          id="verify-otp-code"
          minLength={
            openapi_schema.components.schemas.PostLoginWithOTPEmailRequest
              .properties.code.minLength
          }
          maxLength={
            openapi_schema.components.schemas.PostLoginWithOTPEmailRequest
              .properties.code.maxLength
          }
        />
      </fieldset>
      <ButtonSubmit disabled={!valid || loading}>Log In</ButtonSubmit>
    </form>
  );
}

export { RequestOTP, VerifyOTP };
