import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/api';
import { Button1 } from '../components/Utils/Button';
import { AuthModalsContext } from '../contexts/AuthModals';
import { FileUploader } from '../components/Gallery/FileUploader';

import { GlobalModalsContext } from '../contexts/GlobalModals';
import { Link } from 'react-router-dom';

const API_ENDPOINT = '/home/page/';
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
    endpoint: API_ENDPOINT,
    method: API_METHOD,
  });

  return (
    <div>
      <Link to="/styles/">
        <Button1>Styles</Button1>
      </Link>
      <Link to="/galleries/">
        <Button1>Galleries</Button1>
      </Link>
      <Button1
        onClick={() => {
          globalModalsContext.setModal({
            component: <FileUploader />,
          });
        }}
      >
        Upload Files
      </Button1>
    </div>
  );
}

export { Home };
