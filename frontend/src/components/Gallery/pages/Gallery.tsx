import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../../../contexts/Device';
import { paths, operations, components } from '../../../openapi_schema';
import { ExtractResponseTypes } from '../../../types';
import { useApiCall } from '../../../utils/Api';
import { useParams } from 'react-router-dom';

const API_PATH = '/galleries/{gallery_id}/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Gallery() {
  const { gallery_id } = useParams();
  gallery_id as paths[typeof API_PATH][typeof API_METHOD]['parameters']['path']['gallery_id'];

  let deviceContext = useContext(DeviceContext);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_PATH.replace('{gallery_id}', gallery_id),
      method: API_METHOD,
    },
    true
  );

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];
    return (
      <>
        <h1>Gallery</h1>
        {loading ? <p>Loading...</p> : <p>{data.gallery.name}</p>}
      </>
    );
  }
}

export { Gallery };
