import React from 'react';
import { BaseInputProps } from './Input';

interface InputRadioSetProps<T> extends BaseInputProps<T> {
  name?: string;
}

function InputRadioSet<T extends string>({
  name = null,
  state,
  setState,
  value,
  checked,
  children,
  id,
}: InputRadioSetProps<T>) {
  return (
    <fieldset name={name ?? undefined} id={id}>
      <div>
        <p>asdf</p>
      </div>
    </fieldset>
  );
}

export { InputRadioSet };
