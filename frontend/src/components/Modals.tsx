import React, { useEffect, useRef, useContext } from 'react';
import { CSSTransition } from 'react-transition-group';
import { ModalContext } from '../contexts/Modal';

function Modals() {
  const { state } = useContext(ModalContext);
  return state.stack[state.stack.length - 1];
}

export { Modals };
