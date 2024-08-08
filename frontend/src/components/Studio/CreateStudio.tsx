import React, { useState, useEffect, useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { DataContext } from '../../contexts/Data';
import { createStudioFunc } from './createStudioFunc';

type StudioCreate = components['schemas']['StudioCreate'];

interface Props {
  alwaysActive?: boolean;
}

function CreateStudio({ alwaysActive = false }: Props): JSX.Element {
  function getBlankStudio(): StudioCreate {
    let studio: StudioCreate = {
      name: '',
    };

    return studio;
  }

  const [studio, setStudio] = useState<components['schemas']['StudioCreate']>(
    getBlankStudio()
  );
  const [validCreate, setValidCreate] = useState<boolean>(false);
  const Data = useContext(DataContext);

  // check if studio.name is not empty
  useEffect(() => {
    setValidCreate(studio.name.length > 0);
  }, [studio]);

  // make fieldName one of the keys in StudioCreate
  const handleChange = (fieldName: keyof StudioCreate) => (event) => {
    setStudio({
      ...studio,
      [fieldName]: event.target.value,
    });
  };

  const handleCreate = () => {
    createStudioFunc(studio, Data.studios.dispatch);
    setStudio(getBlankStudio());
  };

  return (
    <div className="card w-fit">
      <h3 className="text-center">Create Studio</h3>
      <label htmlFor="studioName">Name: </label>
      <input
        type="text"
        id="studioName"
        value={studio.name}
        onChange={handleChange('name')}
      />
      <br></br>
      <div className="flex flex-row space-x-2 justify-center mt-2">
        <button
          className="button-secondary"
          onClick={() => setStudio(getBlankStudio())}
        >
          Reset
        </button>
        <button
          className={validCreate ? 'button-valid' : 'button-invalid'}
          onClick={validCreate ? handleCreate : () => null}
        >
          Create
        </button>
      </div>
    </div>
  );
}

export { CreateStudio };
