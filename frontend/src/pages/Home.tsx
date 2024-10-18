import React, { useEffect, useContext, useState } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import { defaultInputState, ExtractResponseTypes, InputState } from '../types';
import { useApiCall } from '../utils/Api';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { InputCheckbox } from '../components/Form/InputCheckbox';
import { InputDatetimeLocal } from '../components/Form/InputDatetimeLocal';
import { InputToggle } from '../components/Form/InputToggle';
import { InputText } from '../components/Form/InputText';
import { Surface } from '../components/Utils/Surface';

const API_PATH = '/home/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_PATH][typeof API_METHOD]['responses']
>;

function Home() {
  let deviceContext = useContext(DeviceContext);
  let toastContext = useContext(ToastContext);
  const authContext = useContext(AuthContext);

  const [toggleState, setToggleState] = useState<InputState<boolean>>({
    ...defaultInputState<boolean>(false),
  });
  const [textState, setTextState] = useState<InputState<string>>({
    ...defaultInputState<string>(''),
  });
  const [dateState, setDateState] = useState<InputState<Date>>({
    ...defaultInputState<Date>(new Date()),
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
      <Surface className="grid grid-cols-2 gap-8 m-4 card">
        <Surface className="card">
          <p>Text in here</p>
        </Surface>
        <Surface className="card">
          <div className="card">
            <p>asdf</p>
            <Surface className="card bg-green-400">
              <div className="bg-inherit p-2">
                <p className="bg-transparent">Text in here</p>
              </div>
            </Surface>
          </div>
          <p>Text in here</p>
        </Surface>
        <Surface className="card">
          <p>Text in here</p>
        </Surface>
        <Surface className="card">
          <p>Text in here</p>
        </Surface>
        <Surface className="card">
          <p>Text in here</p>
        </Surface>
        <button className="button-primary">button here!</button>
        <InputText
          state={textState}
          setState={setTextState}
          id={'text-input-1'}
          type={'text'}
        />
        <InputDatetimeLocal
          state={dateState}
          setState={setDateState}
          id={'datetime-local'}
          type="datetime-local"
          showValidity={true}
        />

        <div className="w-full surface grid grid-cols-2 gap-8 mx-4 my-4 border-2 p-2 card">
          <div className="surface card">
            <p>Text in sadfasdfasdf</p>
            <InputCheckbox
              state={toggleState}
              setState={setToggleState}
              id="checkbox-9"
              type={'checkbox'}
            />
          </div>
          <button className="button-primary">button here!</button>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id="checkbox-4"
            type={'checkbox'}
          />
        </div>
        <InputToggle
          state={toggleState}
          setState={setToggleState}
          id={'checkbox-toggle'}
          type={'checkbox'}
        />
      </Surface>

      <div className="surface mx-4 my-4 p-4 rounded-2xl">
        <p>More text</p>
        <InputToggle
          state={toggleState}
          setState={setToggleState}
          id={'checkbox-toggle-123'}
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

      <div className="surface card m-8">
        <h1>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id={'toggle-sadf'}
            type={'checkbox'}
            showValidity={true}
          />
        </h1>
        <h2>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id={'toggle-2'}
            type={'checkbox'}
          />
        </h2>
        <h3>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id={'toggle-3'}
            type={'checkbox'}
          />
        </h3>
        <h4>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id={'toggle-3'}
            type={'checkbox'}
          />
        </h4>
        <InputCheckbox
          state={toggleState}
          setState={setToggleState}
          id={'toggle-3'}
          type={'checkbox'}
        />

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
