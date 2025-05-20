import React, { useEffect, useContext, useState, useRef } from 'react';
import { DeviceContext } from '../contexts/Device';
import { paths, operations, components } from '../openapi_schema';
import {
  defaultValidatedInputState,
  ModalType,
  ValidatedInputState,
} from '../types';
import { getStylesPage } from '../services/apiServices';
import { useApiCall } from '../utils/api';
import { ToastContext } from '../contexts/Toast';
import { AuthContext } from '../contexts/Auth';
import { ValidatedInputCheckbox } from '../components/Form/ValidatedInputCheckbox';
import { ValidatedInputDatetimeLocal } from '../components/Form/ValidatedInputDatetimeLocal';
import { ValidatedInputToggle } from '../components/Form/ValidatedInputToggle';
import { ValidatedInputString } from '../components/Form/ValidatedInputString';
import { Surface } from '../components/Utils/Surface';
import { ModalsContext } from '../contexts/Modals';

import {
  Button1,
  Button2,
  Button3,
  ButtonSubmit,
} from '../components/Utils/Button';

import { Card1 } from '../components/Utils/Card';
import { Loader1, Loader2, Loader3 } from '../components/Utils/Loader';
import { Checkbox1 } from '../components/Utils/Checkbox';
import { RadioButton1 } from '../components/Utils/RadioButton';
import { useConfirmationModal } from '../utils/useConfirmationModal';
import { Toggle1 } from '../components/Utils/Toggle';
import { AuthModalsContext } from '../contexts/AuthModals';
import { ValidatedInputPhoneNumber } from '../components/Form/ValidatedInputPhoneNumber';
import { E164Number } from 'libphonenumber-js';

export function Styles() {
  let deviceContext = useContext(DeviceContext);
  let toastContext = useContext(ToastContext);
  const authContext = useContext(AuthContext);
  const authModalsContext = useContext(AuthModalsContext);
  const modalsContext = useContext(ModalsContext);
  const { activateButtonConfirmation, activateTextConfirmation } =
    useConfirmationModal();

  const [toggleState, setToggleState] = useState<ValidatedInputState<boolean>>({
    ...defaultValidatedInputState<boolean>(false),
  });
  const [textState, setTextState] = useState<ValidatedInputState<string>>({
    ...defaultValidatedInputState<string>(''),
  });
  const [dateState, setDateState] = useState<ValidatedInputState<Date>>({
    ...defaultValidatedInputState<Date>(new Date()),
  });
  const [radioState, setRadioState] = useState<
    ValidatedInputState<'Option 1' | 'Option 2' | 'Option 3'>
  >({
    ...defaultValidatedInputState<'Option 1' | 'Option 2' | 'Option 3'>(
      'Option 1'
    ),
  });

  const [phoneNumber, setPhoneNumber] = useState<
    ValidatedInputState<E164Number>
  >({
    ...defaultValidatedInputState<E164Number>(null),
  });

  const { data, status, loading } = useApiCall(getStylesPage, {
    authContext,
  });

  const [counter, setCounter] = useState<number>(0);
  const [modalKey, setModalKey] = useState<number>(null);
  const modalKeyRef = useRef<number>(modalKey);

  useEffect(() => {
    modalKeyRef.current = modalKey;
  }, [modalKey]);

  const firstModalRender = useRef(true);

  function ModalTest({
    modalKey,
    counter,
  }: {
    modalKey: number;
    counter: number;
  }) {
    return (
      <div id={`modal-test-${modalKey}`}>
        <h2>Modal</h2>
        <p>Counter: {counter}</p>
        <p>modalKey: {modalKey}</p>
        <div className="flex flex-row space-x-2">
          <Button2
            onClick={() => {
              setCounter((prev) => prev + 1);
            }}
          >
            Increment
          </Button2>
          <Button1 onClick={() => setModalKey((prev) => prev + 1)}>
            Swap modal
          </Button1>
          <Button1
            onClick={() => {
              authModalsContext.activate('logIn');
            }}
          >
            Open Login
          </Button1>
        </div>
      </div>
    );
  }

  useEffect(() => {
    if (modalKey !== null) {
      const key = `modal-test-${modalKey}`;
      const modal: ModalType = {
        key: key,
        Component: ModalTest,
        componentProps: { modalKey, counter },
        onExit: () => {
          setModalKey(null);
        },
      };
      if (modalKey === 0) {
        modalsContext.pushModals([modal]);
      } else {
        modalsContext.swapActiveModal(modal);
      }
      firstModalRender.current = false;
    } else {
      firstModalRender.current = true;
    }
  }, [modalKey]);

  useEffect(() => {
    if (!firstModalRender.current) {
      const key = `modal-test-${modalKey}`;
      modalsContext.updateModals([
        {
          key: key,
          componentProps: { modalKey, counter },
        },
      ]);
    }
  }, [counter]);

  return (
    <div className="p-2">
      <header>
        <h1>Design tokens</h1>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        <section className="flex flex-col space-y-2">
          <Card1>
            <div className="overflow-x-scroll">
              <p>
                asdasdkjaksldjkalsjdkalsjdlkajsdklasjdaksljdlkasdjlkasjdkalsdjklasjkdalskjdlaksjdklasjdlkasjdlkasjdlkasjdlkasjdlkajskdljsa
              </p>
            </div>
          </Card1>
          <Card1 className="flex flex-col ">
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
          <Card1 className="flex flex-col space-y-2">
            <h2>Loaders</h2>
            <div className="flex flex-col border-inherit space-y-2">
              <div className="flex flex-row justify-around">
                <h4>Loader1</h4>
                <h4>Loader2</h4>
                <h4>Loader3</h4>
              </div>

              <div className="flex flex-row justify-around border-inherit border-2 rounded-lg p-2">
                <h1>
                  <Loader1 />
                </h1>
                <h1>
                  <Loader2 />
                </h1>
                <h1 className="mb-0 bg-gray-500">
                  <Loader3 />
                </h1>
              </div>
              <Surface>
                <div className="flex flex-row justify-around border-2 rounded-lg p-2">
                  <h1>
                    <Loader1 />
                  </h1>
                  <h1>
                    <Loader2 />
                  </h1>
                  <h1 className="mb-0 bg-gray-500">
                    <Loader3 />
                  </h1>
                </div>
              </Surface>
            </div>
          </Card1>
          <Card1 className="flex flex-col space-y-2">
            <h2>Modals</h2>
            <p>Counter: {counter}</p>
            <Button2 onClick={() => setCounter((prev) => prev + 1)}>
              Counter ++
            </Button2>
            <Button1
              onClick={() => {
                setModalKey(0);
              }}
            >
              Generate a Modal
            </Button1>
            <Card1>
              <h3 className="mb-2">Confirmation Modals</h3>
              <div className="flex flex-row space-x-2 p-[0.5]">
                <Button2
                  className="flex-1"
                  onClick={() => {
                    activateButtonConfirmation({
                      componentProps: {
                        title: 'Are you sure?',
                        message: 'Example button confirmation modal.',
                        onConfirm: () => {
                          console.log('confirmed');
                        },
                      },
                    });
                  }}
                >
                  Button
                </Button2>
                <Button2
                  className="flex-1"
                  onClick={() => {
                    activateTextConfirmation({
                      componentProps: {
                        message: 'Example text confirmation modal.',
                        target: 'example',
                        title: 'Are you sure?',
                      },
                    });
                  }}
                >
                  Text
                </Button2>
              </div>
            </Card1>
          </Card1>
        </section>
        <section className="flex flex-col space-y-2">
          <Card1 className="flex flex-col space-y-2 overflow-x-auto">
            <form
              action="submit"
              onSubmit={(e) => {
                e.preventDefault();
              }}
              className="flex flex-col space-y-4"
            >
              <header>Form Title</header>
              <fieldset className="space-y-4">
                <section>
                  <label htmlFor="text-input-1">Text Input</label>
                  <ValidatedInputString
                    state={textState}
                    setState={setTextState}
                    id={'text-input-1'}
                    type={'text'}
                    minLength={1}
                    checkValidity={true}
                    isAvailable={async (value) => {
                      await new Promise((resolve) => setTimeout(resolve, 50));
                      return true;
                    }}
                    checkAvailability={true}
                    showStatus={true}
                  />
                </section>
                <section>
                  <label htmlFor="phone-number-input">Phone Number</label>
                  <ValidatedInputPhoneNumber
                    state={phoneNumber}
                    setState={setPhoneNumber}
                  />
                </section>
                <section>
                  <label htmlFor="datetime-local-input-1">
                    Datetime Local Input
                  </label>
                  <ValidatedInputDatetimeLocal
                    state={dateState}
                    setState={setDateState}
                    id={'datetime-local-input-1'}
                  />
                </section>
                <section className="flex flex-row items-end space-x-4 flex-wrap">
                  <h1>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      showStatus={true}
                      inputProps={{
                        id: 'toggle-input-1',
                      }}
                    />
                  </h1>
                  <h2>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-2',
                      }}
                    />
                  </h2>
                  <h3>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-3',
                      }}
                    />
                  </h3>
                  <h4>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-4',
                      }}
                    />
                  </h4>
                  <h5>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-5',
                      }}
                    />
                  </h5>
                  <h6>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-6',
                      }}
                    />
                  </h6>
                  <span className="p mb-0">
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-7',
                      }}
                    />
                  </span>
                  <span>
                    <ValidatedInputToggle
                      state={toggleState}
                      setState={setToggleState}
                      inputProps={{
                        id: 'toggle-input-8',
                      }}
                    />
                  </span>
                  <span>
                    <Toggle1
                      state={toggleState.value}
                      disabled={true}
                    ></Toggle1>
                  </span>
                </section>
                <section className="flex flex-row items-end space-x-4 flex-wrap">
                  <h1>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-1"
                      showStatus={true}
                    />
                  </h1>
                  <h2>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-2"
                    />
                  </h2>
                  <h3>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-3"
                    />
                  </h3>
                  <h4>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-4"
                    />
                  </h4>
                  <h5>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-5"
                    />
                  </h5>
                  <h6>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-6"
                    />
                  </h6>
                  <span>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-7"
                    />
                  </span>
                  <span>
                    <ValidatedInputCheckbox
                      state={toggleState}
                      setState={setToggleState}
                      id="checkbox-input-8"
                    />
                  </span>
                </section>
                <section>
                  <h1>
                    <RadioButton1 state={toggleState.value} />
                  </h1>
                </section>
              </fieldset>
              <ButtonSubmit
                disabled={
                  toggleState.status != 'valid' ||
                  textState.status != 'valid' ||
                  phoneNumber.status != 'valid'
                }
              >
                Submit
              </ButtonSubmit>
            </form>
          </Card1>
          <Card1 className="flex flex-col space-y-2">
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
          <Card1 className="flex flex-col space-y-2">
            <h2 className="mb-12">Headings</h2>
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <h3>Heading 3</h3>
            <h4>Heading 4</h4>
            <h5>Heading 5</h5>
            <h6>Heading 6</h6>
            <p>Paragraph</p>
          </Card1>
        </section>
      </div>
    </div>
  );
}
