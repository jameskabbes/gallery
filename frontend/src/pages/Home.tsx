import React, { useEffect, useState } from 'react';
import privateConfig from '../../private_config.json';

import { useApiData, useConditionalRender } from '../utils/Api';

function Component(data) {
  return (
    <div>
      {data.photos.map((photo) => (
        <img key={photo.id} src={photo.src.medium} alt="" />
      ))}
    </div>
  );
}

function useSetTitle(data): void {
  document.title = 'Home';
}

function Home() {
  const { data, loading } = useApiData({
    endpoint: 'https://api.pexels.com/v1/curated?per_page=9',
    headers: { Authorization: privateConfig.apiKey },
  });
  return useConditionalRender(data, loading, Component, useSetTitle);
}

export { Home };
