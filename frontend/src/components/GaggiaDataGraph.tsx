import { useContext } from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';

export const GaggiaDataGraph = () => {
  const { temperatureReadings } = useContext(GaggiaDataContext);

  return (
    <div>
      <p>Temperature readings: {temperatureReadings.length}</p>
      {temperatureReadings.map((tempReading) => {
        return (
          <p key={tempReading.timestamp.getTime()}>
            {`${tempReading.timestamp.toTimeString()}: ${tempReading.temperature.toLocaleString(
              undefined,
              { maximumFractionDigits: 1 },
            )}`}
          </p>
        );
      })}
    </div>
  );
};
