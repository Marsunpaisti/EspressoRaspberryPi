import { ReactNode, useCallback, useContext, useEffect, useState } from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';
import { DataCard } from './GaggiaDataView';

const EditableValue = ({
  title,
  min,
  max,
  initialValue,
  setValue,
  formatValue,
}: {
  title: ReactNode;
  min: number;
  max: number;
  initialValue: number;
  setValue: (newValue: number) => void;
  formatValue: (value: number) => ReactNode;
}) => {
  const [internalValue, setInternalValue] = useState(initialValue);

  useEffect(() => {
    setInternalValue(initialValue);
  }, [initialValue]);

  const increment = useCallback(() => {
    setInternalValue((prev) => {
      const newValue = prev + 1;
      if (newValue <= max) {
        return newValue;
      } else {
        return prev;
      }
    });
  }, [setInternalValue, max]);

  const decrement = useCallback(() => {
    setInternalValue((prev) => {
      const newValue = prev - 1;
      if (newValue >= min) {
        return newValue;
      } else {
        return prev;
      }
    });
  }, [setInternalValue, min]);

  return (
    <div className="w-full flex flex-col items-center my-2 mx-4 select-none">
      <p className="font-bold w-full text-center relative text-xl">{title}</p>
      <div className="flex flex-row justify-center items-center flex-1 h-full rounded-lg mt-4 text-center max-h-[100px] w-full">
        <div className="text-2xl flex w-full flex-row justify-between items-center">
          <span
            className="flex material-symbols-outlined cursor-pointer bg-stone-500 p-2 rounded-lg select-none"
            onClick={decrement}
          >
            remove
          </span>
          <span className="text-[30px]">{formatValue(internalValue)}</span>
          <span
            className="flex material-symbols-outlined cursor-pointer bg-stone-500 p-2 rounded-lg select-none"
            onClick={increment}
          >
            add
          </span>
        </div>
      </div>
      {internalValue !== initialValue && (
        <div className="flex flex-row w-full gap-3">
          <button
            className="bg-red-900 py-1 px-4 rounded-lg mt-4 flex-1 flex justify-center"
            onClick={() => {
              setInternalValue(initialValue);
            }}
          >
            Cancel
          </button>
          <button
            className="bg-green-900 py-1 px-4 rounded-lg mt-4 flex-1 flex justify-center"
            onClick={() => {
              setValue(internalValue);
            }}
          >
            Ok
          </button>
        </div>
      )}
    </div>
  );
};
export const GaggiaConfigView = () => {
  const { gaggiaConfig, setSteamSetpoint, setShotTimeLimit, setBrewSetpoint } =
    useContext(GaggiaDataContext);

  return (
    <div className="flex flex-col items-center">
      <div className="flex flex-col max-w-[300px] gap-3 text-xl">
        <DataCard>
          <EditableValue
            title={
              <span className="w-full px-8">
                <span className="material-symbols-outlined absolute left-[-0px] top-0 bottom-0 text-[1.5em]">
                  coffee
                </span>
                Brew setpoint
              </span>
            }
            min={80}
            max={110}
            initialValue={gaggiaConfig.brewSetpoint}
            setValue={setBrewSetpoint}
            formatValue={(value) => `${value} °C`}
          />
        </DataCard>
        <DataCard>
          <EditableValue
            title={
              <span className="w-full px-8">
                <span className="material-symbols-outlined absolute left-[-0px] top-0 bottom-0 text-[1.5em]">
                  air
                </span>
                Steam setpoint
              </span>
            }
            min={120}
            max={160}
            initialValue={gaggiaConfig.steamSetpoint}
            setValue={setSteamSetpoint}
            formatValue={(value) => `${value} °C`}
          />
        </DataCard>
        <DataCard>
          <EditableValue
            title={
              <span className="w-full px-8">
                <span className="material-symbols-outlined absolute left-[-0px] top-0 bottom-0 text-[1.5em]">
                  timer
                </span>
                Shot time limit
              </span>
            }
            min={0}
            max={45}
            initialValue={gaggiaConfig.shotTimeLimit}
            setValue={setShotTimeLimit}
            formatValue={(value) => `${value} s`}
          />
        </DataCard>
      </div>
    </div>
  );
};
