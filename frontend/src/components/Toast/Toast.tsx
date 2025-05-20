import React, { useState, useEffect, useContext, useRef } from 'react';
import { ToastContext } from '../../contexts/Toast';
import { DeviceContext } from '../../contexts/Device';

import { CSSTransition, TransitionGroup } from 'react-transition-group';

import { IoCheckmark } from 'react-icons/io5';
import { IoAlert } from 'react-icons/io5';
import { IoWarning } from 'react-icons/io5';
import { ToastType } from '../../types';
import tailwindConfig from '../../../tailwind.config';
import { Card1 } from '../Utils/Card';
import { Loader1, Loader2 } from '../Utils/Loader';
import { zIndex } from '../../config/constants';

const IconMapping: Map<ToastType['type'], React.ReactNode> = new Map([
  ['success', <IoCheckmark />],
  ['info', <IoAlert />],
  ['error', <IoWarning />],
  ['pending', <Loader1 />],
]);

const height = 60;

// Change according values in the Toast.css file
const timeouts = {
  enter: 100,
  exit: 0,
  move: 0,
};
const lifetime = 3000;

export function Toast() {
  const toastContext = useContext(ToastContext);
  const deviceContext = useContext(DeviceContext);

  return (
    <div
      id="toast-container"
      className="fixed bottom-4 right-4 flex flex-col space-y-2 w-80"
      style={{
        zIndex: zIndex.toast,
      }}
    >
      <TransitionGroup>
        {Array.from(toastContext.state.toasts.keys()).map((toastId) => {
          let toast = toastContext.state.toasts.get(toastId);

          if (toast.type !== 'pending') {
            setTimeout(() => {
              toastContext.dispatch({
                type: 'REMOVE',
                payload: toastId,
              });
            }, lifetime);
          }

          return (
            <CSSTransition key={toastId} classNames="toast" timeout={timeouts}>
              <Card1
                id={`toast-${toastId}`}
                className="card flex flex-row items-center space-x-1 m-2 shadow-xl overflow-clip"
                style={{ height: `${height}px` }}
                onClick={() => {
                  toastContext.dispatch({ type: 'REMOVE', payload: toastId });
                }}
              >
                <p
                  className="rounded-full p-1 text-light leading-none"
                  style={{
                    backgroundColor:
                      toast.type !== 'pending' &&
                      tailwindConfig.theme.extend.colors[toast.type]['500'],
                    animation:
                      toast.type !== 'pending' && 'scaleUp 0.2s ease-in-out',
                  }}
                >
                  <span>{IconMapping.get(toast.type)}</span>
                </p>
                <p>{toast.message}</p>
              </Card1>
            </CSSTransition>
          );
        })}
      </TransitionGroup>
    </div>
  );
}
