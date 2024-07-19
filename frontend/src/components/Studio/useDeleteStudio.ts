// useDeleteStudio.ts
import { useContext } from 'react';
import { ConfirmationModalContext } from '../../contexts/ConfirmationModal';
import { callApi } from '../../utils/Api';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

function useDeleteStudio(studioId: string) {
  const context = useContext(ConfirmationModalContext);

  function handleDeleteClick() {
    context.dispatch({ type: 'RESET' });
    context.dispatch({ type: 'SET_TITLE', payload: 'Delete Studio' });
    context.dispatch({
      type: 'SET_MESSAGE',
      payload: 'Are you sure you want to delete this studio?',
    });
    context.dispatch({ type: 'SET_IS_ACTIVE', payload: true });
    console.log(context);

    callApi(API_PATH.replace('{studio_id}', studioId), API_METHOD);

    // Optionally, call the API here if you want the deletion to be initiated immediately upon confirmation
    // callApi(API_PATH.replace('{studio_id}', studioId), API_METHOD);
  }

  return handleDeleteClick;
}

export { useDeleteStudio };
