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

const API_ENDPOINT = '/galleries/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

interface AddGalleryProps {}

function AddGallery({}: AddGalleryProps) {
  const [name, setName] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  const [date, setDate] = useState<ValidatedInputState<Date>>(
    defaultValidatedInputState<Date>(new Date())
  );

  const [description, setDescription] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });

  const [visibility, setVisibility] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>('private'),
  });

  async function addGallery(event: React.FormEvent) {
    event.preventDefault();
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
              state={date}
              setState={setDate}
              id="gallery-date"
              required={true}
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
                  .description.maxLength
              }
              required={true}
              checkValidity={true}
              showStatus={true}
            />
          </section>
        </fieldset>
        <ButtonSubmit>Add Gallery</ButtonSubmit>
      </form>
    </div>
  );
}

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
    </div>
  );
}

export { Galleries };
