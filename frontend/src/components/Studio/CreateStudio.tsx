import React, { useState } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { callApi } from '../../utils/Api';
import { DataContext } from '../../contexts/Data';

type StudioCreate = components['schemas']['StudioCreate'];
const API_PATH = '/studios/';

function CreateStudio() {
  function getBlankStudio(): StudioCreate {
    let studio: StudioCreate = {
      name: '',
    };

    return studio;
  }

  const { addStudio } = React.useContext(DataContext);
  const [studio, setStudio] = useState<components['schemas']['StudioCreate']>(
    getBlankStudio()
  );

  const handleChange = (fieldName) => (event) => {
    setStudio({
      ...studio,
      [fieldName]: event.target.value,
    });
  };

  const handleCancel = () => {
    setStudio(getBlankStudio());
  };

  const handleCreate = () => {
    addStudio(studio);
    setStudio(getBlankStudio());
  };

  return (
    <div>
      <label htmlFor="studioName">Name: </label>
      <input
        type="text"
        id="studioName"
        value={studio.name}
        onChange={handleChange('name')}
      />
      <br></br>
      <button onClick={handleCancel}>Cancel</button>
      <button onClick={handleCreate}>Create</button>
    </div>
  );
}

export { CreateStudio };
