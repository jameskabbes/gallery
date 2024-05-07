import React, { useState, useEffect } from 'react';
import { callApi, useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studio/';

function Studio(): JSX.Element {
  return <h1>Studio</h1>;
}

export { Studio };
