import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/Api';
import {
  StudiosReducerAction,
  ConfirmationModalContextShowModal,
} from '../../types';

import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function deleteStudioFunc(
  studio: components['schemas']['StudioPublic'],
  studiosDispatch: React.Dispatch<StudiosReducerAction>,
  showConfirmationModal: ConfirmationModalContextShowModal
) {
  const isConfirmed = await showConfirmationModal(
    'Delete Studio',
    'Are you sure you want to delete this studio?'
  );

  if (!isConfirmed) return;

  let toastId = toast.loading('Deleting studio');
  studiosDispatch({ type: 'DELETE', payload: studio.id });
  const { data, status } = await callApi<
    AllResponseTypes[keyof AllResponseTypes]
  >(API_PATH.replace('{studio_id}', studio.id), API_METHOD);

  if (status === 204) {
    const apiData = data as AllResponseTypes['204'];
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Studio Deleted',
      type: 'success',
    });
  } else {
    studiosDispatch({ type: 'ADD', payload: studio });
    toast.update(toastId, {
      ...toastTemplate,
      render: 'Could not delete studio',
      type: 'error',
    });
  }
}

export { deleteStudioFunc };
