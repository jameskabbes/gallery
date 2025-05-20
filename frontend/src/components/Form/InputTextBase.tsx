import React, { useEffect, useRef } from 'react';

type InputTextBaseInputProps = Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  'onChange'
>;

export interface InputTextBaseProps extends InputTextBaseInputProps {
  value: InputTextBaseInputProps['value'];
  setValue: (value: InputTextBaseInputProps['value']) => void;
}

export function InputTextBase({ setValue, ...rest }: InputTextBaseProps) {
  return (
    <input
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(e.target.value);
      }}
      {...rest}
    />
  );
}
