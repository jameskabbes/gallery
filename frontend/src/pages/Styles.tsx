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

import {
  Button1,
  Button2,
  Button3,
  ButtonSubmit,
} from '../components/Utils/Button';

import { Card1 } from '../components/Utils/Card';
import { Loader1, Loader2, Loader3 } from '../components/Utils/Loader';

function Styles() {
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

  return (
    <div>
      <header>
        <h1>Styles</h1>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2">
        <section className="flex-1">
          <Card1 className="m-2">
            <h2>Buttons</h2>
            <div className="flex flex-row space-x-2">
              <div className="flex-1 flex flex-col space-y-4">
                <Button1>Button1</Button1>
                <Button2>Button2</Button2>
                <Button3>Button3</Button3>
                <ButtonSubmit>ButtonSubmit</ButtonSubmit>
              </div>
              <div className="flex-1 flex flex-col space-y-4">
                <Button1 disabled={true}>Button1</Button1>
                <Button2 disabled={true}>Button2</Button2>
                <Button3 disabled={true}>Button3</Button3>
                <ButtonSubmit disabled={true}>ButtonSubmit</ButtonSubmit>
              </div>
            </div>
          </Card1>
          <Card1 className="flex flex-col space-y-2 m-2">
            <h2>Loaders</h2>
            <div className="flex flex-col border-inherit space-y-2">
              <div className="flex flex-row justify-around">
                <h4>Loader1</h4>
                <h4>Loader2</h4>
                <h4>Loader3</h4>
              </div>

              <div className="flex flex-row justify-around border-inherit border-2 rounded-lg p-2">
                <h1 className="mb-0">
                  <Loader1 />
                </h1>
                <h1 className="mb-0">
                  <Loader2 />
                </h1>
                <h1 className="mb-0 bg-primary-light dark:bg-primary-dark">
                  <Loader3 />
                </h1>
              </div>
              <Surface>
                <div className="flex flex-row justify-around border-2 rounded-lg p-2">
                  <h1 className="mb-0">
                    <Loader1 />
                  </h1>
                  <h1 className="mb-0">
                    <Loader2 />
                  </h1>
                  <h1 className="mb-0 bg-primary-light dark:bg-primary-dark">
                    <Loader3 />
                  </h1>
                </div>
              </Surface>
            </div>
          </Card1>
        </section>
        <section className="flex-1 flex-col">
          <Card1 className="flex flex-col space-y-2 m-2">
            <form
              action="submit"
              onSubmit={(e) => {
                e.preventDefault();
              }}
              className="flex flex-col space-y-6"
            >
              <header>Form Title</header>
              <section className="space-y-2">
                <label htmlFor="text-input-1">Text Input</label>
                <InputText
                  state={textState}
                  setState={setTextState}
                  id={'text-input-1'}
                  type={'text'}
                  minLength={1}
                  checkValidity={true}
                />
              </section>
              <section className="space-y-2">
                <label htmlFor="datetime-local">Datetime Local Input</label>
                <InputDatetimeLocal
                  state={dateState}
                  setState={setDateState}
                  id={'datetime-local'}
                  type="datetime-local"
                  showValidity={true}
                />
              </section>

              <section className="space-y-2">
                <label htmlFor="toggle-1">Toggle Input</label>
                <InputToggle
                  state={toggleState}
                  setState={setToggleState}
                  id={'toggle-1'}
                  type={'checkbox'}
                  showValidity={true}
                />
              </section>
              <section className="space-y-2">
                <label htmlFor="checkbox-1">Checkbox Input</label>
                <InputCheckbox
                  state={toggleState}
                  setState={setToggleState}
                  id={'checkbox-1'}
                  type={'checkbox'}
                  showValidity={true}
                />
              </section>
              <ButtonSubmit
                disabled={
                  toggleState.status != 'valid' || textState.status != 'valid'
                }
              >
                Submit
              </ButtonSubmit>
            </form>
          </Card1>
          <Card1 className="flex flex-col space-y-2 m-2">
            <h2>Toast</h2>

            <Button1
              onClick={() => {
                let toastId = toastContext.makePending({
                  message: 'making toast',
                });
                const toastTypes = ['error', 'info', 'success'] as const;
                const randomIndex = Math.floor(
                  Math.random() * toastTypes.length
                );

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
          </Card1>
        </section>
      </div>
    </div>
  );
}

export default Styles;
