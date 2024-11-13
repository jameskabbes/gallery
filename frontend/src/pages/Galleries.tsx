import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/api';
import { Button1 } from '../components/Utils/Button';
import { AuthContext } from '../contexts/Auth';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { setGalleryModal } from '../components/Gallery/AddGallery';
import { GalleryCardButton } from '../components/Gallery/CardButton';
import { LogInPromptFullPage } from '../components/LogInPromptFullPage';
import { PostGalleryResponses } from '../services/api/postGallery';

const API_ENDPOINT = '/galleries/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Galleries() {
  const authContext = useContext(AuthContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  const [galleries, setGalleries] = useState<
    ResponseTypesByStatus['200']['galleries']
  >({});

  const { data, loading, status, refetch } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >(
    {
      url: API_ENDPOINT,
      method: API_METHOD,
    },
    [authContext.state]
  );

  useEffect(() => {
    if (data && status === 200) {
      setGalleries((data as ResponseTypesByStatus['200']).galleries);
    }
  }, [data]);

  if (loading) {
    return null;
  } else if (!authContext.state.user) {
    return <LogInPromptFullPage />;
  } else if (status === 200) {
    return (
      <div>
        <Button1
          onClick={() => {
            setGalleryModal(
              globalModalsContext,
              (gallery: PostGalleryResponses['200']) => {
                setGalleries((galleries) => {
                  galleries[gallery.id] = gallery;
                  return { ...galleries };
                });
              }
            );
          }}
        >
          Add Gallery
        </Button1>
        <div className="flex flex-wrap">
          {Object.keys(galleries).map((galleryId) => (
            <div className="p-2" key={galleryId}>
              <GalleryCardButton
                gallery={galleries[galleryId]}
              ></GalleryCardButton>
            </div>
          ))}
        </div>
      </div>
    );
  } else {
    return null;
  }
}

export { Galleries };
