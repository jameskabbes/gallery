import React from 'react';
import { CallApiProps } from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/users/{user_id}/sessions/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Sessions(): JSX.Element {
  return (
    <div>
      <h2>Sessions</h2>
      <p>Manage your sessions here.</p>
    </div>
  );
}

export { Sessions };
