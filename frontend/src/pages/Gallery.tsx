import React, { useEffect, useContext, useState, Children } from 'react';
import { useParams } from 'react-router-dom';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultValidatedInputState, ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/api';
import { GlobalModalsContext } from '../contexts/GlobalModals';
import { AuthContext } from '../contexts/Auth';
import { Button1 } from '../components/Utils/Button';
import { setFileUploaderModal } from '../components/Gallery/FileUploader';

import { IoCloudUploadOutline } from 'react-icons/io5';
import { setGalleryModal } from '../components/Gallery/AddGallery';
import { getGalleryLink } from '../components/Gallery/getLink';
import { Link } from 'react-router-dom';

const API_ENDPOINT = '/galleries/{gallery_id}/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface Props {
  root?: boolean;
}

function Gallery({ root = false }: Props) {
  const globalModalsContext = useContext(GlobalModalsContext);
  const authContext = useContext(AuthContext);

  const galleryId: components['schemas']['Gallery']['id'] =
    useParams().galleryId;

  const { data, loading, status } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >(
    {
      url: API_ENDPOINT.replace('{gallery_id}', galleryId),
      method: API_METHOD,
      params: {
        root: root,
      },
    },
    [galleryId]
  );

  if (loading) {
    return <div>Loading...</div>;
  } else {
    if (status === 200) {
      const apiData = data as ResponseTypesByStatus['200'];
      return (
        <>
          <div className="flex flex-row space-x-2 ">
            {apiData.parents.map((gallery, index) => (
              <span key={gallery.id} className="flex flex-row space-x-2">
                <Link to={getGalleryLink(gallery.id)}>
                  <p className="underline" key={gallery.id}>
                    {gallery.name}
                  </p>
                </Link>
                <p>/</p>
              </span>
            ))}
          </div>
          <div className="flex flex-row justify-between items-center">
            <h1>{apiData.gallery.name}</h1>
            <Button1
              onClick={() =>
                setGalleryModal({
                  globalModalsContext,
                  onSuccess: (gallery) => {
                    console.log(gallery);
                  },
                  parentGalleryId: apiData.gallery.id,
                })
              }
            >
              Make Gallery
            </Button1>
            <Button1
              onClick={() =>
                setFileUploaderModal(globalModalsContext, apiData.gallery)
              }
            >
              <div className="flex flex-row items-center space-x-2">
                <IoCloudUploadOutline />
                Upload Files
              </div>
            </Button1>
          </div>
          <div>
            {apiData.children.map((gallery) => (
              <div key={gallery.id}>
                <Link to={getGalleryLink(gallery.id)}>
                  <p className="underline" key={gallery.id}>
                    {gallery.name}
                  </p>
                </Link>
              </div>
            ))}
          </div>
        </>
      );
    } else {
      return <div>Gallery not found</div>;
    }
  }
}

export { Gallery };
