import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { StudiosReducerAction } from '../../types';
import { toast } from 'react-toastify';

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

  const { data, status } = await callApi<
    AllResponseTypes[keyof AllResponseTypes]
  >(API_PATH, API_METHOD, studio);

  if (status === 200) {
    const apiData = data as AllResponseTypes['200'];
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    studios_dispatch({ type: 'ADD', payload: apiData });
    toast.update(toastId, {
      render: 'Studio created',
      type: 'success',
      isLoading: false,
      autoClose: 5000,
    });
  } else {
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    console.error('Error creating studio:', status, data);
    toast.update(toastId, {
      render: 'Could not create studio',
      type: 'error',
      isLoading: false,
      autoClose: 5000,
    });
  }
}

export { createStudioFunc };
