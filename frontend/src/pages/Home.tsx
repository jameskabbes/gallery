import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultInputState, ExtractResponseTypes, InputState } from '../types';
import { useApiCall } from '../utils/Api';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { InputCheckbox } from '../components/Form/InputCheckbox';

const API_PATH = '/home/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Home() {
  let deviceContext = useContext(DeviceContext);
  let toastContext = useContext(ToastContext);
  const authContext = useContext(AuthContext);

  const [state, setState] = useState<InputState<boolean>>({
    ...defaultInputState<boolean>(false),
  });

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

  return (
    <div>
      <h1>Test again</h1>
      {/* <h1 className='loader'></h1>
      <h1 className='loader-secondary'></h1> */}

      {authContext.state.user ? (
        <p>Logged in as {authContext.state.user.email}</p>
      ) : (
        <p>not logged in</p>
      )}

      <button
        className="button-primary"
        onClick={() => {
          let toastId = toastContext.makePending({ message: 'making toast' });
          const toastTypes = ['error', 'info', 'success'] as const;
          const randomIndex = Math.floor(Math.random() * toastTypes.length);

          setTimeout(() => {
            toastContext.update(toastId, {
              message: 'made toast',
              type: toastTypes[randomIndex],
              // choose random from options
            });
          }, 2000);
        }}
      >
        Add Random Toast
      </button>
      <InputCheckbox
        state={state}
        setState={setState}
        id={'checkbox'}
        type={'checkbox'}
      />
      <div className="card m-8">
        <h1>h1</h1>
        <h2>h2</h2>
        <h3>h3</h3>
        <h4>h4</h4>
        <h5>h5</h5>
        <h6>h6</h6>
        <button className="button-primary">hello there</button>
        <button className="button-primary" disabled={true}>
          hello there
        </button>
        <button className="button-secondary">hello there</button>
        <button className="button-secondary" disabled={true}>
          hello there
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-primary-lighter h-64"></div>
        <div className="bg-primary h-64"></div>
        <div className="bg-primary-darker h-64"></div>
        <div className="bg-secondary-lighter h-64"></div>
        <div className="bg-secondary h-64"></div>
        <div className="bg-secondary-darker h-64"></div>
        <div className="bg-accent-lighter h-64"></div>
        <div className="bg-accent h-64"></div>
        <div className="bg-accent-darker h-64"></div>
        <div className="bg-light-lighter h-64"></div>
        <div className="bg-light h-64"></div>
        <div className="bg-light-darker h-64"></div>
        <div className="bg-dark-lighter h-64"></div>
        <div className="bg-dark h-64"></div>
        <div className="bg-dark-darker h-64"></div>
      </div>
    </div>
  );
}

export { Home };
