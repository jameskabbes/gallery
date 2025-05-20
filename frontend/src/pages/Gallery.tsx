import React, { useEffect, useContext, useState, Children } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { useApiCall } from '../utils/api';
import { ModalsContext } from '../contexts/Modals';
import { AuthContext } from '../contexts/Auth';
import { Button1 } from '../components/Utils/Button';
import { setFileUploaderModal } from '../components/Gallery/FileUploader';

import {
  deleteGallery,
  getGalleryPage,
  postGallerySync,
} from '../services/apiServices';

import { IoCloudUploadOutline } from 'react-icons/io5';
import { setAddGalleryModal } from '../components/Gallery/AddGallery';
import { getGalleryLink } from '../components/Gallery/getLink';
import { Link } from 'react-router-dom';
import { ToastContext } from '../contexts/Toast';
import { config } from '../config/config';

interface Props {
  root?: boolean;
}

export function Gallery({ root = false }: Props) {
  const modalsContext = useContext(ModalsContext);
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const navigate = useNavigate();

  const galleryId: components['schemas']['GalleryPrivate']['id'] =
    useParams().galleryId;

  const { data, loading, status, refetch } = useApiCall(
    getGalleryPage,
    {
      authContext,
      pathParams: {
        gallery_id: galleryId,
      },
      params: {
        root: root,
      },
    },
    [galleryId]
  );

  async function handleSyncGallery(
    gallery: components['schemas']['GalleryPublic']
  ) {
    let toastId = toastContext.makePending({
      message: `Syncing gallery ${gallery.date ? `${gallery.date} ` : ''}${
        gallery.name
      }`,
    });
    const response = await postGallerySync.call({
      pathParams: {
        gallery_id: gallery.id,
      },
    });
    if (response.status === 200) {
      toastContext.update(toastId, {
        message: 'Gallery synced with local',
        type: 'success',
      });
      refetch();
    } else {
      toastContext.update(toastId, {
        message: 'Error syncing gallery with local',
        type: 'error',
      });
      refetch();
    }
  }

  async function handleDeleteGallery(
    gallery: components['schemas']['GalleryPublic']
  ) {
    let toastId = toastContext.makePending({
      message: `Delete gallery ${gallery.date} ${gallery.name}`,
    });
    const response = await deleteGallery.call({
      pathParams: {
        gallery_id: gallery.id,
      },
    });

    if (response.status === 204) {
      toastContext.update(toastId, {
        message: 'Gallery deleted',
        type: 'success',
      });
      navigate(config.frontendRoutes.galleries);
    } else {
      toastContext.update(toastId, {
        message: 'Error deleting gallery',
        type: 'error',
      });
    }
  }

  if (loading) {
    return <div>Loading...</div>;
  } else {
    if (status === 200) {
      const apiData = data as (typeof getGalleryPage.responses)['200'];
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
                setAddGalleryModal({
                  modalsContext,
                  onSuccess: (gallery) => {
                    refetch();
                  },
                  parentGalleryId: apiData.gallery.id,
                })
              }
            >
              Make Gallery
            </Button1>
            <Button1
              onClick={() =>
                setFileUploaderModal(modalsContext, apiData.gallery)
              }
            >
              <div className="flex flex-row items-center space-x-2">
                <IoCloudUploadOutline />
                Upload Files
              </div>
            </Button1>
            <Button1 onClick={() => handleSyncGallery(apiData.gallery)}>
              Sync with Local
            </Button1>
            <Button1
              onClick={() => handleDeleteGallery(apiData.gallery)}
              disabled={apiData.gallery.parent_id === null}
            >
              Delete Gallery
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
