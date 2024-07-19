import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import { StudiosReducerAction } from '../../types';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function deleteStudioFunc(
  studio: components['schemas']['StudioPublic'],
  studios_dispatch: React.Dispatch<StudiosReducerAction>
) {
  console.log('calling delete');
  console.log(studio);
  studios_dispatch({ type: 'DELETE', payload: studio.id });
  const { data, status } = await callApi<
    AllResponseTypes[keyof AllResponseTypes]
  >(API_PATH.replace('{studio_id}', studio.id), API_METHOD);

  if (status === 204) {
    const apiData = data as AllResponseTypes['204'];
  } else {
    studios_dispatch({ type: 'ADD', payload: studio });
  }
}

export { deleteStudioFunc };
