import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callBackendApi } from '../../utils/api';
import { StudiosReducerAction } from '../../types';
import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast/Toast';

const API_PATH = '/studios/';
const API_METHOD = 'post';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function createStudioFunc(
  studio: components['schemas']['StudioCreate'],
  studios_dispatch: React.Dispatch<StudiosReducerAction>
) {
  let publicStudio: components['schemas']['StudioPublic'] = {
    ...studio,
    id: '__loading__',
  };

  let toastId = toast.loading('Creating studio');
  studios_dispatch({ type: 'ADD', payload: publicStudio });

  const { data, response } = await callBackendApi<
    AllResponseTypes[keyof AllResponseTypes],
    components['schemas']['StudioCreate']
  >({
    endpoint: API_PATH,
    method: API_METHOD,
    data: studio,
  });

  if (response.status === 200) {
    const apiData = data as AllResponseTypes['200'];
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    studios_dispatch({ type: 'ADD', payload: apiData });
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Studio created',
      type: 'success',
    });
  } else {
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    console.error('Error creating studio:', response.status, data);
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Could not create studio',
      type: 'error',
    });
  }
}

export { createStudioFunc };
