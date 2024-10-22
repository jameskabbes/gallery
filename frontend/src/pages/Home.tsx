import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultInputState, ExtractResponseTypes, InputState } from '../types';
import { useApiCall } from '../utils/Api';

const API_PATH = '/home/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Home() {
  return <p>Home</p>;
}

export { Home };
