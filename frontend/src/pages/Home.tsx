import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import {
  defaultValidatedInputState,
  ExtractResponseTypes,
  ValidatedInputState,
} from '../types';
import { useApiCall } from '../utils/api';
import { Button1, Button2 } from '../components/Utils/Button';
import { AuthModalsContext } from '../contexts/AuthModals';
import { FileUploader } from '../components/Gallery/FileUploader';

import { GlobalModalsContext } from '../contexts/GlobalModals';
import { Link } from 'react-router-dom';
import { Modal } from '../components/Modal/Modal';

const API_ENDPOINT = '/pages/home/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Home() {
  const authModalsContext = useContext(AuthModalsContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  const { data } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
  });

  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div>
        <Link to="/styles/">
          <Button1>Styles</Button1>
        </Link>
        <Button2 onClick={() => setShowModal(true)}>Show Modal</Button2>
      </div>
      <Modal onExit={() => setShowModal(false)} modalKey="asdf">
        {showModal && (
          <div>
            <p>hello</p>
            <Button1 onClick={() => authModalsContext.activate('logIn')}>
              Open Login
            </Button1>
          </div>
        )}
      </Modal>
    </>
  );
}

export { Home };
