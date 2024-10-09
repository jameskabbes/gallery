import React, { useState, useEffect, useContext, useRef } from 'react';
import { ToastContext } from '../../contexts/Toast';
import { DeviceContext } from '../../contexts/Device';

import { CSSTransition, TransitionGroup } from 'react-transition-group';

import { IoCheckmark } from 'react-icons/io5';
import { IoAlert } from 'react-icons/io5';
import { IoWarning } from 'react-icons/io5';
import { Toast } from '../../types';
import './Toast.css';
import tailwindConfig from '../../../tailwind.config';

const IconMapping: Map<Toast['type'], React.ReactNode> = new Map([
  ['success', <IoCheckmark />],
  ['info', <IoAlert />],
  ['error', <IoWarning />],
  ['pending', <span className="loader"></span>],
]);

const height = 60;

// Change according values in the Toast.css file
const timeouts = {
  enter: 100,
  exit: 0,
  move: 0,
};
const lifetime = 3000;

function Toast() {
  const toastContext = useContext(ToastContext);
  const deviceContext = useContext(DeviceContext);

  return (
    <div id="toast-container">
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
              <div
                id={toastId}
                className="toast m-2"
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
              </div>
            </CSSTransition>
          );
        })}
      </TransitionGroup>
    </div>
  );
}

export { Toast };
