import React, { useEffect, useState } from 'react';
import privateConfig from '../private_config.json';

async function callApi(endpoint: string) {
  console.log('Calling API: ' + endpoint);
  const response = await fetch(endpoint, {
    method: 'GET',
    headers: { Authorization: privateConfig.apiKey },
  });

  try {
    return response.json();
  } catch {
    return {};
  }
}

function Home(): JSX.Element {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await callApi(
          'https://api.pexels.com/v1/curated?per_page=9'
        );
        setData(result);
        setLoading(false);
        console.log(data);
      } catch (error) {
        console.error(error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <p>loading...</p>;
  } else {
    return (
      <>
        <p>not loading</p>
        <div>
          {data.photos.map((photo) => (
            <img src={photo.src.tiny} alt="" />
          ))}
        </div>
      </>
    );
  }
}

export { Home };
