import React, { useContext, useEffect, useRef, useState } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { useApiCall } from '../../utils/Api';
import { AuthContext } from '../../contexts/Auth';
import { UpdatePassword } from './UpdatePassword';
import { UpdateUser } from './UpdateUser';
import { AuthModalsContext } from '../../contexts/AuthModals';
import { UpdateUsername } from './UpdateUsername';
import { Button1 } from '../Utils/Button';

const API_PATH = '/profile/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Profile() {
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_PATH,
      method: API_METHOD,
    },
    true
  );

  console.log(apiData, loading, response);

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];

    if (loading) {
      return <p>loading</p>;
    }

    return (
      <div>
        <h1>{data.user.username}</h1>
        <div className="w-80">
          {/* <UpdateUser user={apiData.user} />
          <UpdatePassword userId={apiData.user.id} />
          <UpdateUsername user={apiData.user} /> */}
        </div>
      </div>
    );
  } else {
    return (
      <div className="h-full w-full flex flex-col justify-center items-center">
        <div className="flex-row justify-center">
          <Button1
            onClick={() => authModalsContext.setActiveModalType('logIn')}
          >
            Login to continue
          </Button1>
        </div>
      </div>
    );
  }
}

export { Profile };
