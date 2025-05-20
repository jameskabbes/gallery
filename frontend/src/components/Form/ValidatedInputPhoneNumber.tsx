import React, { useEffect, useState } from 'react';
import {
  parsePhoneNumberFromString,
  AsYouType,
  CountryCode,
  E164Number,
} from 'libphonenumber-js';
import metadata from 'libphonenumber-js/metadata.min.json';

import { InputTextBase, InputTextBaseInputProps } from './InputTextBase';
import { CheckOrX } from './CheckOrX';
import {
  useValidatedInputString,
  UseValidatedInputStringProps,
} from '../../utils/useValidatedInput';
import { Surface } from '../Utils/Surface';

type T = E164Number;

export interface ValidatedInputPhoneNumberProps
  extends UseValidatedInputStringProps,
    InputTextBaseInputProps {
  defaultCountryCode?: CountryCode; // Default country code (e.g., 'US', 'GB')
  showStatus?: boolean;
}

export function ValidatedInputPhoneNumber({
  state,
  setState,
  checkAvailability,
  checkValidity,
  isValid,
  isAvailable,
  defaultCountryCode = 'US',
  className = '',
  showStatus = true,
  ...rest
}: ValidatedInputPhoneNumberProps) {
  useValidatedInputString({
    state,
    setState,
    checkAvailability,
    checkValidity,
    isValid,
    isAvailable,
  });

  const [selectedCountryCode, setSelectedCountryCode] =
    useState<CountryCode>(defaultCountryCode);
  const [display, setDisplay] = useState<string>('');
  const [displayProposedChange, setDisplayProposedChange] =
    useState<string>('');
  const [countryOptions, setCountryOptions] = useState<
    {
      code: CountryCode;
      name: string;
    }[]
  >([]);

  // Get the user's language
  const userLanguage = navigator.language || 'en-US';

  useEffect(() => {
    const displayNames = new Intl.DisplayNames(userLanguage, {
      type: 'region',
    });

    // Map and sort country names
    const sortedCountries = Object.keys(metadata.countries)
      .map((countryCode: CountryCode) => ({
        code: countryCode,
        name: displayNames.of(countryCode) || countryCode,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));

    setCountryOptions(sortedCountries);
  }, [userLanguage]);

  useEffect(() => {
    const formatter = new AsYouType(selectedCountryCode);

    const a = formatter.input(displayProposedChange);
    setDisplay(a);

    const phoneNumber = parsePhoneNumberFromString(
      displayProposedChange,
      selectedCountryCode
    );

    if (phoneNumber && phoneNumber.isValid()) {
      setState((prev) => ({
        ...prev,
        value: phoneNumber.number, // Store in E.164 format
        status: 'valid',
        error: null,
      }));
    } else {
      setState((prev) => ({
        ...prev,
        value: a,
        status: 'invalid',
        error: 'Invalid phone number',
      }));
    }
  }, [displayProposedChange, selectedCountryCode]);

  return (
    <div className="flex flex-row space-x-2">
      <Surface>
        <div className="flex flex-1 flex-row items-center space-x-2 input-phone-number-container">
          <Surface>
            <select
              value={selectedCountryCode}
              onChange={(e) =>
                setSelectedCountryCode(e.target.value as CountryCode)
              }
              className="[prefers-color-scheme:dark] rounded-md max-w-[160px]"
            >
              {countryOptions.map((countryOption) => {
                return (
                  <option key={countryOption.code} value={countryOption.code}>
                    (+{metadata.countries[countryOption.code][0]}){' '}
                    {countryOption.name}
                  </option>
                );
              })}
            </select>
          </Surface>

          <InputTextBase
            value={display}
            setValue={(value: string) => setDisplayProposedChange(value)}
            className={'dark:[color-scheme:dark]' + className}
            {...rest}
          />
          {showStatus && (
            <span title={state.error || ''}>
              <CheckOrX status={state.status} />
            </span>
          )}
        </div>
      </Surface>
    </div>
  );
}
