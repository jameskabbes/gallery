import React, { useEffect, useContext, useState } from 'react';
import { useParams } from 'react-router-dom';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultValidatedInputState, ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/api';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { AuthContext } from '../contexts/Auth';
import { Button1 } from '../components/Utils/Button';
import { setFileUploaderModal } from '../components/Gallery/FileUploader';

const API_ENDPOINT = '/galleries/{gallery_id}/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Gallery() {
  const galleryId: components['schemas']['Gallery']['id'] =
    useParams().galleryId;
  const globalModalsContext = useContext(GlobalModalsContext);
  const authContext = useContext(AuthContext);

  const { data, loading, status } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    url: API_ENDPOINT.replace('{gallery_id}', galleryId),
    method: API_METHOD,
  });

  if (loading) {
    return <div>Loading...</div>;
  } else {
    if (status === 200) {
      const apiData = data as ResponseTypesByStatus['200'];
      return (
        <>
          <div className="flex flex-row justify-between items-center">
            <h1>{apiData.gallery.name}</h1>
            <div>
              <Button1
                onClick={() =>
                  setFileUploaderModal(globalModalsContext, apiData.gallery)
                }
              >
                Upload Files
              </Button1>
            </div>
          </div>
        </>
      );
    } else {
      return <div>Gallery not found</div>;
    }
  }
}

export { Gallery };
