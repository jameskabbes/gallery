import React, { useState, useEffect } from 'react';
import {
  postAPIKey,
  ResponseTypesByStatus as PostAPIKeyResponseTypes,
} from '../../../services/api/postAPIKey';
import { paths, operations, components } from '../../../openapi_schema';

function AddAPIKey() {
  const [name, setName] =
    useState<components['schemas']['APIKeyCreate']['name']>('');
  const [expiry, setExpiry] = useState<Date>(new Date());

  async function addAPIKey() {
    globalModalsContext.setModal(null);
    let toastId = toastContext.makePending({
      message: 'Creating API Key...',
    });

    // make a random 16 character string
    const tempID = Array.from(
      { length: 16 },
      () => Math.random().toString(36)[2]
    ).join('');

    const tempAPIKey: PostAPIKeyResponseTypes['200'] = {
      id: tempID,
      user_id: authContext.state.user.id,
      expiry: expiry.toISOString(),
      issued: new Date().toISOString(),
      name: name,
    };

    setAPIKeys((prevAPIKeys) => ({
      ...prevAPIKeys,
      [tempID]: tempAPIKey,
    }));

    const { data, response } = await postAPIKey({
      expiry: expiry.toISOString(),
      name: name,
    });

    if (response.status === 200) {
      const apiData = data as PostAPIKeyResponseTypes['200'];
      toastContext.update(toastId, {
        message: `Created API Key ${apiData.name}`,
        type: 'success',
      });

      setAPIKeys((prevAPIKeys) => {
        const newAPIKeys = { ...prevAPIKeys };
        delete newAPIKeys[tempID];
        newAPIKeys[apiData.id] = apiData;
        return newAPIKeys;
      });
    } else {
      toastContext.update(toastId, {
        message: 'Error creating API Key',
        type: 'error',
      });

      setAPIKeys((prevAPIKeys) => {
        const newAPIKeys = { ...prevAPIKeys };
        delete newAPIKeys[tempID];
        return newAPIKeys;
      });
    }
  }

  return (
    <div id="add-api-key">
      <h3>Add API Key</h3>
      <form onSubmit={() => {}} className="flex flex-col space-y-2">
        <div className="flex flex-row items-center space-x-2">
          <label htmlFor="api-key-name">Name</label>
          <input
            id="api-key-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="flex flex-row items-center space-x-2">
          <label htmlFor="api-key-expiry">Expiry</label>
          <input
            className="flex flex-row text-input"
            id="api-key-expiry"
            type="date"
            value={expiry.toISOString().split('T')[0]}
            onChange={(e) => setExpiry(new Date(e.target.value))}
          />
        </div>

        <button onClick={addAPIKey} className="button-primary" type="submit">
          <span className="flex flex-row text-center">Add API Key</span>
        </button>
      </form>
    </div>
  );
}
