import React from 'react';
import { useApiData, useConditionalRender } from '../utils/Api';
import privateConfig from '../../private_config.json';
import { Photo } from '../types';
import { Gallery } from '../components/Gallery/Gallery';

type HomePageApi = {
  photos: Photo[];
};

function Component(data: HomePageApi) {
  return <Gallery photos={data.photos} />;
}

function useSetTitle(data: HomePageApi): void {
  document.title = 'Home';
}

function Home() {
  const { data, loading } = useApiData<HomePageApi>({
    endpoint: 'https://api.pexels.com/v1/curated?per_page=9',
    headers: { Authorization: privateConfig.apiKey },
  });
  return useConditionalRender(data, loading, Component, useSetTitle);
}

export { Home };
