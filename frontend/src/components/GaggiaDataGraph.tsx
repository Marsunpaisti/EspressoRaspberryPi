import { useContext } from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';

export const GaggiaDataGraph = () => {
  const { temperatureReadings } = useContext(GaggiaDataContext);

  return (
    <div>
      <p>Temperature readings: {temperatureReadings.length}</p>
    </div>
  );
};
