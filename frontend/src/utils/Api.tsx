import React, { useState, useEffect } from 'react';
import axios, { AxiosResponse, AxiosError } from 'axios';

type callApiParams = {
  endpoint: string;
  method?: string;
  headers?: object;
  data?: object;
};

//utility func to make API calls
async function callApi({
  endpoint,
  method = 'GET',
  headers = {},
  data = null,
}: callApiParams) {
  try {
    const response = await axios({
      method,
      url: endpoint,
      headers,
      data,
    });

    return response.data;
  } catch (error) {
    console.error('Error calling API: ', error.message);
    return {};
  }
}

function useApiData<T>(callApiParams_: callApiParams): {
  data: T | null;
  loading: boolean;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await callApi(callApiParams_);
        setData(result);
        setLoading(false);
      } catch (error) {
        console.error(error);
        setLoading(false);
      }
    }
    fetchData();
  }, [callApiParams_]);

  return { data, loading };
}

type UseEffectOnLoadFn = (data: any) => void;

function useConditionalRender(
  data: any,
  loading: boolean,
  ComponentIfLoaded: React.FC<any>,
  useEffectOnLoad: UseEffectOnLoadFn = (data: any) => {}
) {
  useEffect(() => {
    if (!loading) {
      if (data) {
        useEffectOnLoad(data);
      }
    }
  }, [loading]);

  if (loading) {
    return <p>Loading...</p>;
  } else {
    if (data) {
      return ComponentIfLoaded(data);
    } else {
      return <p>Data not Available</p>;
    }
  }
}

export { callApi, useApiData, useConditionalRender };
