import React, { useEffect, useContext, useState } from 'react';
import { useParams } from 'react-router-dom';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultValidatedInputState, ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/Api';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { AuthContext } from '../contexts/Auth';

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

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_ENDPOINT.replace('{gallery_id}', galleryId),
    method: API_METHOD,
  });

  if (loading) {
    return <div>Loading...</div>;
  } else {
    if (response.status === 200) {
      const data = apiData as ResponseTypesByStatus['200'];
      return (
        <div>
          <h1>{data.gallery.name}</h1>
          <p>{data.gallery.description}</p>
        </div>
      );
    } else {
      return <div>Gallery not found</div>;
    }
  }
}

export { Gallery };
