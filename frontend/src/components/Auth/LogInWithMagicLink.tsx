import React, { useContext, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { ModalsContext } from '../../contexts/Modals';
import { Loader1 } from '../Utils/Loader';
import { IoWarning } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';
import { postLogInWithMagicLink } from '../../services/api/postLogInWithMagicLink';
import { AuthContext } from '../../contexts/Auth';

function LogInWithMagicLink() {
  const location = useLocation();
  const authContext = useContext(AuthContext);
  const searchParams = new URLSearchParams(location.search);
  const [status, setStatus] = useState<number>(null);
  const access_token: string = searchParams.get('access_token');
  const stay_signed_in = searchParams.get('stay_signed_in') === 'True';
  const modalsContext = useContext(ModalsContext);
  const modalKey = 'modal-verify-magic-link';

  useEffect(() => {
    async function verifyMagicLink() {
      setStatus(null);
      const { status } = await postLogInWithMagicLink(authContext, {
        access_token: access_token,
      });
      setStatus(status);
    }

    verifyMagicLink();
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

export { LogInWithMagicLink };
