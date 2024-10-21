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
import Button1 from '../components/Utils/Button/Button1';
import Button2 from '../components/Utils/Button/Button2';
import Button from '../components/Utils/Button/Button';

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
    <Surface>
      <div className="grid grid-cols-2 gap-8 m-4 card">
        <Surface>
          <div className="card">
            <p>Text in here</p>
          </div>
        </Surface>
        <Surface>
          <div className="card">
            <p>Text in here</p>
          </div>
        </Surface>
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
        <Button1>Button1</Button1>
        <Button2>Button2</Button2>

        {/* <div className="flex flex-row">
          <h4 className="mb-0">
            <Surface className="p-2 border-2 rounded-full flex flex-row">
              <Surface className="loader1"></Surface>
            </Surface>
          </h4>
          <div className="flex-1"></div>
        </div> */}
      </div>
    </Surface>
  );

  /* <Surface className="bg-green-500  dark:bg-green-500 p-4">
          <p>sadfasdasf</p>
        </Surface>

        <h4>
          <Surface className="loader2"></Surface>
        </h4>

        <Surface className="w-full surface grid grid-cols-2 gap-8 card">
          <h2>
            <Surface className="loader1"></Surface>
          </h2>

          <Surface className="card">
            <p>Text in sadfasdfasdf</p>
            <InputCheckbox
              state={toggleState}
              setState={setToggleState}
              id="checkbox-9"
              type={'checkbox'}
            />
          </Surface>
          <Button1>another button here</Button1>
          <Button2>another button here</Button2>
          <Button1>another button here</Button1>
          <InputCheckbox
            state={toggleState}
            setState={setToggleState}
            id="checkbox-4"
            type={'checkbox'}
          />
        </Surface>
        <InputToggle
          state={toggleState}
          setState={setToggleState}
          id={'checkbox-toggle'}
          type={'checkbox'}
        />
      </Surface>

      <Surface className="card mx-4">
        <p>More text</p>
        <InputToggle
          state={toggleState}
          setState={setToggleState}
          id={'checkbox-toggle-123'}
          type={'checkbox'}
          showValidity={true}
        />
      </Surface>

      <Button1
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
      </Button1>

      {authContext.state.user ? (
        <p>Logged in as {authContext.state.user.email}</p>
      ) : (
        <p>not logged in</p>
      )}

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
        <button className="button1">hello there</button>
        <button className="button1" disabled={true}>
          hello there
        </button>
        <button className="button-secondary">hello there</button>
        <button className="button-secondary" disabled={true}>
          hello there
        </button> */
}

export { Home };
