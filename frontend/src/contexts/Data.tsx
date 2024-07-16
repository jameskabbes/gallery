import React, { useState, useEffect, createContext } from 'react';
import { DataContext as DataContextType } from '../types';
import { components } from '../openapi_schema';
import { generateRandomStringId } from '../utils/randomString';
import { callApi } from '../utils/Api';

const defaultContextValue: DataContextType = {
  studios: new Map(),
  addStudio: () => {},
  removeStudio: () => {},
};

const DataContext = createContext<DataContextType>({
  ...defaultContextValue,
});

interface Props {
  children: React.ReactNode;
}

function DataContextProvider({ children }: Props) {
  const [studios, setStudios] = useState<DataContextType['studios']>(
    defaultContextValue.studios
  );

  function addStudio(studio: components['schemas']['StudioCreate']) {
    let randomId: components['schemas']['StudioID'];
    while (true) {
      randomId = generateRandomStringId();
      if (!studios.has(randomId)) {
        break;
      }
    }

    let studioPublic: components['schemas']['StudioPublic'] = {
      ...studio,
      id: randomId,
    };

    setStudios((prevStudios) =>
      new Map(prevStudios).set(randomId, studioPublic)
    );

    // callApi to create studio, then update the studio with the response, remove if it doesn't pay off
  }

  function removeStudio(studioId: components['schemas']['StudioID']) {
    if (studios.has(studioId)) {
      studios.delete(studioId);
      setStudios(new Map(studios));
      return true;
    }
    return false;
  }

  return (
    <DataContext.Provider
      value={{
        studios,
        addStudio,
        removeStudio,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export { DataContext, DataContextProvider };
