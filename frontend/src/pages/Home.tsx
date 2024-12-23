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

import { Link } from 'react-router-dom';

const API_ENDPOINT = '/pages/home/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Home() {
  const authModalsContext = useContext(AuthModalsContext);

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
    </>
  );
}

export { Home };
