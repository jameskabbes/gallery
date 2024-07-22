import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes, ToastContextAddToast } from '../../types';
import { callApi } from '../../utils/Api';
import {
  StudiosReducerAction,
  ConfirmationModalContextShowModal,
} from '../../types';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function deleteStudioFunc(
  studio: components['schemas']['StudioPublic'],
  studiosDispatch: React.Dispatch<StudiosReducerAction>,
  showConfirmationModal: ConfirmationModalContextShowModal,
  addToast: ToastContextAddToast
) {
  const isConfirmed = await showConfirmationModal(
    'Delete Studio',
    'Are you sure you want to delete this studio?'
  );

  console.log('isConfirmed', isConfirmed);

  if (!isConfirmed) return;

  studiosDispatch({ type: 'DELETE', payload: studio.id });
  const { data, status } = await callApi<
    AllResponseTypes[keyof AllResponseTypes]
  >(API_PATH.replace('{studio_id}', studio.id), API_METHOD);

  if (status === 204) {
    const apiData = data as AllResponseTypes['204'];
    addToast({
      message: 'Studio deleted',
      type: 'success',
    });
  } else {
    studiosDispatch({ type: 'ADD', payload: studio });
  }
}

export { deleteStudioFunc };
