import React, { useState, useEffect, useContext } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { DataContext } from '../../contexts/Data';
import { createStudioFunc } from './createStudioFunc';

type StudioCreate = components['schemas']['StudioCreate'];

function CreateStudio() {
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

  const handleCancel = () => {
    setStudio(getBlankStudio());
  };

  const handleCreate = () => {
    createStudioFunc(studio, Data.studios.dispatch);
    setStudio(getBlankStudio());
  };

  return (
    <div>
      <label htmlFor="studioName">Name: </label>
      <input
        className="border-2 border-black"
        type="text"
        id="studioName"
        value={studio.name}
        onChange={handleChange('name')}
      />
      <br></br>
      <button onClick={handleCancel}>Cancel</button>
      <button
        className={validCreate ? 'button-valid' : 'button-invalid'}
        onClick={validCreate ? handleCreate : () => null}
      >
        Create
      </button>
    </div>
  );
}

export { CreateStudio };
