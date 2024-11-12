import React, { useContext, useState, useEffect } from 'react';
import {
  GlobalModalsContextType,
  Modal,
  ValidatedInputState,
  defaultValidatedInputState,
} from '../../types';
import { paths, operations, components } from '../../openapi_schema';
import {
  postGallery,
  PostGalleryResponses,
} from '../../services/api/postGallery';

import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { GlobalModalsContext } from '../../contexts/GlobalModals';

import { ValidatedInputString } from '../Form/ValidatedInputString';
import { ValidatedInputDatetimeLocal } from '../Form/ValidatedInputDatetimeLocal';
import { ButtonSubmit } from '../Utils/Button';
import openapi_schema from '../../../../openapi_schema.json';
import config from '../../../../config.json';

interface AddGalleryProps {
  onSuccess: (gallery: PostGalleryResponses['200']) => void;
}

function AddGallery({ onSuccess }: AddGalleryProps) {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const globalModalsContext = useContext(GlobalModalsContext);

  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  const [parentGallery, setParentGallery] = useState<
    ValidatedInputState<components['schemas']['Gallery']>
  >({
    ...defaultValidatedInputState<components['schemas']['Gallery']>(null),
  });

  const [datetime, setDatetime] = useState<ValidatedInputState<Date | null>>(
    defaultValidatedInputState<Date | null>(null)
  );

  const [description, setDescription] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  const [visibilityLevelName, setVisibilityLevelName] = useState<
    ValidatedInputState<string>
  >({
    ...defaultValidatedInputState<string>('private'),
  });

  const [valid, setValid] = useState(false);
  useEffect(() => {
    setValid(
      name.status === 'valid' &&
        parentGallery.status === 'valid' &&
        datetime.status === 'valid' &&
        description.status === 'valid' &&
        visibilityLevelName.status === 'valid'
    );
  }, [
    name.status,
    parentGallery.status,
    datetime.status,
    description.status,
    visibilityLevelName.status,
  ]);

  async function addGallery(event: React.FormEvent) {
    event.preventDefault();
    globalModalsContext.setModal(null);

    const toastId = toastContext.makePending({
      message: 'Adding gallery...',
    });

    const galleryCreate = {
      name: name.value,
      parent_id: parentGallery.value ? parentGallery.value.id : null,
      datetime: datetime['value'] ? datetime['value'].toISOString() : null,
      description: description.value,
      visibility_level:
        config['visibility_level_name_mapping'][visibilityLevelName.value],
    };
    console.log(galleryCreate);

    const { data, status } = await postGallery(authContext, galleryCreate);
    if (status === 200) {
      toastContext.update(toastId, {
        message: 'Gallery added',
        type: 'success',
      });
      console.log(data);
      onSuccess(data as PostGalleryResponses['200']);
    } else {
      toastContext.update(toastId, {
        message: 'Error adding gallery',
        type: 'error',
      });
    }
  }

  return (
    <div id="add-gallery">
      <form onSubmit={addGallery} className="flex flex-col space-y-4">
        <header>Add Gallery</header>
        <fieldset>
          <section>
            <label htmlFor="gallery-name">Name</label>
            <ValidatedInputString
              state={name}
              setState={setName}
              id="gallery-name"
              type="text"
              minLength={
                openapi_schema.components.schemas.GalleryCreate.properties.name
                  .minLength
              }
              maxLength={
                openapi_schema.components.schemas.GalleryCreate.properties.name
                  .maxLength
              }
              required={true}
              checkValidity={true}
              showStatus={true}
            />
          </section>
          <section>
            <label htmlFor="gallery-date">Date</label>
            <ValidatedInputDatetimeLocal
              state={datetime}
              setState={setDatetime}
              id="gallery-date"
              showStatus={true}
            />
          </section>
          <section>
            <label htmlFor="gallery-description">Description</label>
            <ValidatedInputString
              state={description}
              setState={setDescription}
              id="gallery-description"
              type="text"
              minLength={
                openapi_schema.components.schemas.GalleryCreate.properties
                  .description.anyOf[0].minLength
              }
              maxLength={
                openapi_schema.components.schemas.GalleryCreate.properties
                  .description.anyOf[0].maxLength
              }
              checkValidity={true}
              showStatus={true}
            />
          </section>
        </fieldset>
        <ButtonSubmit disabled={!valid}>Add Gallery</ButtonSubmit>
      </form>
    </div>
  );
}

function setGalleryModal(
  globalModalsContext: GlobalModalsContextType,
  onSuccess: (gallery: PostGalleryResponses['200']) => void
) {
  globalModalsContext.setModal({
    component: <AddGallery onSuccess={onSuccess} />,
    key: 'add-gallery',
  });
}

export { AddGallery, setGalleryModal };
