import React, { useContext, useEffect, useRef } from 'react';
import { paths, operations, components } from '../../../openapi_schema';
import { ExtractResponseTypes } from '../../../types';
import { useApiCall } from '../../../utils/Api';
import { AuthContext } from '../../../contexts/Auth';
import { InputText } from '../../Form/InputText';
import { UpdatePassword } from '../UpdatePassword';
import { UpdateUser } from '../UpdateUser';

const API_PATH = '/pages/profile/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Profile() {
  const authContext = useContext(AuthContext);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_PATH,
      method: API_METHOD,
    },
    true,
    [authContext.state.auth?.user?.username]
  );

  if (loading || response.status == 200) {
    const data = apiData as ResponseTypesByStatus['200'];

    if (loading) {
      return <p>loading</p>;
    }

    return (
      <div>
        <h1>{data.user.username}</h1>
        <div className="w-80">
          <UpdateUser user={data.user} />
          <UpdatePassword userId={data.user.id} />
        </div>
      </div>
    );
  } else {
    return <p>Login to continue</p>;
  }
}

export { Profile };
