import React, { Component, useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  ExtractResponseTypes,
  ModalsContext as ModalsContextType,
} from '../../types';
import { callBackendApi } from '../../utils/Api';
import { StudiosReducerAction } from '../../types';
import { ConfirmationModal } from '../ConfirmationModal';

import { toast } from 'react-toastify';
import { toastTemplate } from '../Toast/Toast';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

async function deleteStudioFunc(
  studio: components['schemas']['StudioPublic'],
  studiosDispatch: React.Dispatch<StudiosReducerAction>,
  modalContext: ModalsContextType
) {
  async function onConfirm() {
    let toastId = toast.loading('Deleting studio');
    studiosDispatch({ type: 'DELETE', payload: studio.id });
    const { data, response } = await callBackendApi<
      AllResponseTypes[keyof AllResponseTypes]
    >({
      endpoint: API_PATH.replace('{studio_id}', studio.id),
      method: API_METHOD,
    });
    console.log('got it back');

    if (response.status === 204) {
      const apiData = data as AllResponseTypes['204'];
      toast.update(toastId, {
        ...toastTemplate,
        render: `Studio ${studio.name} deleted`,
        type: 'success',
      });
    } else {
      studiosDispatch({ type: 'ADD', payload: studio });
      toast.update(toastId, {
        ...toastTemplate,
        render: `Could not delete studio ${studio.name}`,
        type: 'error',
      });
    }
  }

  modalContext.dispatch({
    type: 'PUSH',
    payload: React.createElement(ConfirmationModal, {
      key: 'delete-studio',
      title: 'Delete Studio',
      message: 'Are you sure you want to delete this studio?',
      onConfirm: onConfirm,
      onCancel: () => {},
    }),
  });
}

export { deleteStudioFunc };
