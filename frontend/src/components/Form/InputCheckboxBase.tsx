import React, { useState, useEffect } from 'react';

export type InputCheckboxBaseInputProps = Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  'type' | 'onChange'
>;

export interface InputCheckboxBaseProps extends InputCheckboxBaseInputProps {
  checked: InputCheckboxBaseInputProps['checked'];
  setChecked: (checked: InputCheckboxBaseInputProps['checked']) => void;
}

export function InputCheckboxBase({
  setChecked,
  ...rest
}: InputCheckboxBaseProps) {
  return (
    <input
      type="checkbox"
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        setChecked(e.target.checked);
      }}
      {...rest}
    />
  );
}
