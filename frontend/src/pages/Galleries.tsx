import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultValidatedInputState, ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/Api';
import { Button1, ButtonSubmit } from '../components/Utils/Button';
import { Link } from 'react-router-dom';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { AuthContext } from '../contexts/Auth';
import { ValidatedInputState } from '../types';
import { ValidatedInputString } from '../components/Form/ValidatedInputString';
import openapi_schema from '../../../openapi_schema.json';
import { ValidatedInputDatetimeLocal } from '../components/Form/ValidatedInputDatetimeLocal';
import { AddGallery } from '../components/Gallery/AddGallery';
import { Card1 } from '../components/Utils/Card';
import { GalleryCardButton } from '../components/Gallery/CardButton';

const API_ENDPOINT = '/galleries/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Galleries() {
  const globalModalsContext = useContext(GlobalModalsContext);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
  });

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <Button1
        onClick={() => {
          globalModalsContext.setModal({
            component: <AddGallery />,
          });
        }}
      >
        Add Gallery
      </Button1>
      <div className="flex flex-wrap">
        {Object.keys(apiData.galleries).map((galleryId) => (
          <div className="p-2" key={galleryId}>
            <GalleryCardButton
              gallery={apiData.galleries[galleryId]}
            ></GalleryCardButton>
          </div>
        ))}
      </div>
    </div>
  );
}

export { Galleries };
