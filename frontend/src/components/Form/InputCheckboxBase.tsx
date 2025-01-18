import React, { useState, useEffect } from 'react';

type InputCheckboxBaseInputProps = Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  'type' | 'onChange'
>;

interface InputCheckboxBaseProps extends InputCheckboxBaseInputProps {
  checked: InputCheckboxBaseInputProps['checked'];
  setChecked: (checked: InputCheckboxBaseInputProps['checked']) => void;
}

function InputCheckboxBase({ setChecked, ...rest }: InputCheckboxBaseProps) {
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

export {
  InputCheckboxBase,
  InputCheckboxBaseInputProps,
  InputCheckboxBaseProps,
};
