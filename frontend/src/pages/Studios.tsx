import React from 'react';
import { useApiData } from '../utils/Api';
import { paths, operations, components } from '../openapi_schema';

const API_PATH = '/studios/';

function Studios(): JSX.Element {
  const [data, setData, loading, setLoading, status, setStatus] =
    useApiData<
      paths[typeof API_PATH]['get']['responses']['200']['content']['application/json']
    >(API_PATH);

  console.log(data);

  return (
    <div>
      <h1>Studios</h1>
      {data && (
        <ul>
          {Object.keys(data.studios).map((key) => (
            <li key={key}>
              {data.studios[key].name} {data.studios[key].dir_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export { Studios };
