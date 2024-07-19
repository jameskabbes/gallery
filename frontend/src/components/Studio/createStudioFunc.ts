import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { StudiosReducerAction } from '../../types';

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

  studios_dispatch({ type: 'ADD', payload: publicStudio });

  const { data, status } = await callApi<
    AllResponseTypes[keyof AllResponseTypes]
  >(API_PATH, API_METHOD, studio);

  if (status === 200) {
    const apiData = data as AllResponseTypes['200'];
    // sleep for 2 seconds
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    studios_dispatch({ type: 'ADD', payload: apiData });
  } else {
    studios_dispatch({ type: 'DELETE', payload: '__loading__' });
    console.error('Error creating studio:', status, data);
  }
}

export { createStudioFunc };
