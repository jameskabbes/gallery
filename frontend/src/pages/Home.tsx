import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultInputState, ExtractResponseTypes, InputState } from '../types';
import { useApiCall } from '../utils/Api';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { InputCheckbox } from '../components/Form/InputCheckbox';
import { InputDatetimeLocal } from '../components/Form/InputDatetimeLocal';
import { Input } from '../components/Form/Input';
import { Toggle } from '../components/Utils/Toggle';
import { InputToggle } from '../components/Form/InputToggle';

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

  const [state2, setState2] = useState<InputState<Date>>({
    ...defaultInputState<Date>(new Date()),
  });

  const [toggleState, setToggleState] = useState<InputState<boolean>>({
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
      <div className="surface grid grid-cols-2 gap-8 m-4 card">
        <div className="surface card">
          <p>Text in here</p>
        </div>
        <div className="surface card">
          <p>Text in here</p>
        </div>
        <div className="surface card">
          <p>Text in here</p>
        </div>
        <div className="surface card">
          <p>Text in here</p>
        </div>
        <div className="surface card">
          <p>Text in here</p>
        </div>
        <button className="button-primary">button here!</button>
        <div className="w-full surface grid grid-cols-2 gap-8 mx-4 my-4 border-2 p-2 card">
          <div className="surface card">
            <p>Text in here</p>
          </div>
          <div className="surface card">
            <p>Text in here</p>
          </div>
          <div className="surface card">
            <p>Text in here</p>
          </div>
          <div className="surface card">
            <p>Text in here</p>
          </div>
          <div className="surface card">
            <p>Text in here</p>
          </div>
          <button className="button-primary">button here!</button>
        </div>
      </div>

      <InputToggle
        state={state}
        setState={setState}
        id={'checkbox-toggle'}
        type={'checkbox'}
      />

      <div className="surface mx-4 my-4 p-4 rounded-2xl">
        <p>More text</p>
        <InputToggle
          state={state}
          setState={setState}
          id={'checkbox-toggle'}
          type={'checkbox'}
          showValidity={true}
        />
      </div>

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

      {authContext.state.user ? (
        <p>Logged in as {authContext.state.user.email}</p>
      ) : (
        <p>not logged in</p>
      )}

      <InputCheckbox
        state={state}
        setState={setState}
        id={'checkbox'}
        type={'checkbox'}
      />
      <p>{state.value}</p>
      <InputDatetimeLocal
        state={state2}
        setState={setState2}
        id={'datetime-local'}
        type="datetime-local"
        showValidity={true}
      />
      <Toggle
        state={toggleState.value}
        handleToggle={() =>
          setToggleState((prevState) => ({
            ...prevState,
            value: !prevState.value,
          }))
        }
      />

      {state2.value instanceof Date ? (
        <p>{state2.value.toUTCString()}</p>
      ) : (
        <p>Invalid date</p>
      )}

      <button
        className="button-primary"
        onClick={() => {
          setState2((prevState) => ({
            ...prevState,
            value: new Date(
              prevState.value.getTime() + 7 * 24 * 60 * 60 * 1000
            ),
          }));
        }}
      >
        Increment Date by 7 Days
      </button>

      <div className="surface card m-8">
        {/* <h1>
          <Toggle
            state={toggleState['value']}
            handleToggle={() =>
              setToggleState((prevState) => ({
                ...prevState,
                value: !prevState.value,
              }))
            }
          />
        </h1>
        <p>
          <Toggle
            state={toggleState['value']}
            handleToggle={() =>
              setToggleState((prevState) => ({
                ...prevState,
                value: !prevState.value,
              }))
            }
          />
        </p> */}

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
    </div>
  );
}

export { Home };
