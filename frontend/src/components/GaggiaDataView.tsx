import { useContext } from 'react';
import {
  GaggiaDataContext,
  TemperatureReading,
} from '../contexts/GaggiaDataContext';
import { scaleTime, scaleLinear } from '@visx/scale';
import { extent, max } from 'd3-array';
import { LinePath } from '@visx/shape';

const getX = (d: TemperatureReading) => d.timestamp;
const getY = (d: TemperatureReading) => d.temperature;
const TemperatureChart = ({ data }: { data: TemperatureReading[] }) => {
  const xScale = scaleTime({
    domain: extent(data, getX) as [Date, Date],
  });
  const yScale = scaleLinear<number>({
    domain: [0, max(data, getY) as number],
  });
  return <svg width={500} height={500} fill="#FF0000"></svg>;
};

export const GaggiaDataView = () => {
  const { temperatureReadings, socketConnected } =
    useContext(GaggiaDataContext);

  return (
    <div className="w-full flex flex-1 flex-col items-center">
      <p>{socketConnected ? 'Connected' : 'Connecting...'}</p>
      <p>Temperature readings: {temperatureReadings.length}</p>
      <TemperatureChart data={temperatureReadings} />
    </div>
  );
};
