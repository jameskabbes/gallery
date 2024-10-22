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

import Button from '../components/Utils/Button/Button';
import Button1 from '../components/Utils/Button/Button1';
import Button2 from '../components/Utils/Button/Button2';
import Button3 from '../components/Utils/Button/Button3';
import ButtonSubmit from '../components/Utils/Button/ButtonSubmit';
import Card from '../components/Utils/Card/Card';
import Loader1 from '../components/Utils/Loader/Loader1';
import Loader2 from '../components/Utils/Loader/Loader2';

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
          <Card className="flex flex-col space-y-2 m-4">
            <h2>Buttons</h2>

            <Button>Button</Button>
            <Button1>Button1</Button1>
            <Button2>Button2</Button2>
            <Button3>Button3</Button3>
            <ButtonSubmit>ButtonSubmit</ButtonSubmit>
          </Card>
          <Card className="flex flex-col space-y-2 m-4">
            <h2>Loaders</h2>
            <div className="flex flex-col border-inherit space-y-2">
              <div className="flex flex-row justify-around">
                <h4>Loader1</h4>
                <h4>Loader2</h4>
              </div>

              <div className="flex flex-row justify-around border-inherit border-2 rounded-lg p-2">
                <h1 className="mb-0">
                  <Loader1 />
                </h1>
                <h1 className="mb-0">
                  <Loader2 />
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
                </div>
              </Surface>
            </div>
          </Card>
        </section>
        <section className="flex-1 flex-col">
          <Card className="flex flex-col space-y-2 m-4">
            <h2>Forms</h2>
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
          </Card>
          <Card className="flex flex-col space-y-2 m-4">
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
          </Card>
        </section>
      </div>
    </div>
  );
}

export default Styles;
