// useDeleteStudio.ts
import { useContext } from 'react';
import { ConfirmationModalContext } from '../../contexts/ConfirmationModal';
import { callApi } from '../../utils/Api';

const API_PATH = '/studios/{studio_id}/';
const API_METHOD = 'delete';

function useDeleteStudio(studioId: string) {
  const context = useContext(ConfirmationModalContext);

  const handleDeleteClick = () => {
    console.log('clicked!');
    context.setTitle('Delete Studio');
    context.setMessage('Are you sure you want to delete this studio?');
    context.setIsActive(true);

    console.log(context);

    // Optionally, call the API here if you want the deletion to be initiated immediately upon confirmation
    // callApi(API_PATH.replace('{studio_id}', studioId), API_METHOD);
  };

  return handleDeleteClick;
}

export { useDeleteStudio };
