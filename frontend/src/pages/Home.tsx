import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/Api';
import { Button1 } from '../components/Utils/Button';
import { AuthModalsContext } from '../contexts/AuthModals';

const API_PATH = '/home/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Home() {
  const authModalsContext = useContext(AuthModalsContext);

  return (
    <Button1 onClick={() => authModalsContext.setActiveModalType('logIn')}>
      Login
    </Button1>
  );
}

export { Home };
