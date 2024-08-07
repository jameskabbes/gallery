import React, { useEffect } from 'react';
import { useBackendApiCall, useApiCall, callApi } from '../utils/Api';

function Home() {
  const { data, loading, response } = useBackendApiCall({
    method: 'GET',
    endpoint: '/studios/',
  });

  useEffect(() => {
    if (!loading) {
      console.log(data);
    }
  }, [loading]);

  return <p>{loading ? 'loading' : 'not loading'}</p>;
}

export { Home };
