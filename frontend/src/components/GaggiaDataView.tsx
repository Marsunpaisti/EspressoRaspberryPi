import { useContext } from 'react';
import {
  GaggiaDataContext,
  ITelemetryData,
} from '../contexts/GaggiaDataContext';
import { scaleTime, scaleLinear } from '@visx/scale';
import { extent, max, min } from 'd3-array';
import { Group } from '@visx/group';
import { LinePath } from '@visx/shape';
import { SpinnerView } from './MainRouter';
import { GridRows, GridColumns } from '@visx/grid';
import { AxisLeft, AxisBottom } from '@visx/axis';
import useMeasure from 'react-use-measure';

const getX = (d: ITelemetryData) => d.timestamp;
const getY = (d: ITelemetryData) => d.temperature;
const TemperatureChart = ({
  temperatureReadings,
  timeHorizonMs,
}: {
  temperatureReadings: ITelemetryData[];
  timeHorizonMs: number;
}) => {
  const [ref, bounds] = useMeasure();

  const latestTemperatureData =
    temperatureReadings[temperatureReadings.length - 1] ?? -1;
  const temperatureData = temperatureReadings.filter(
    (data) =>
      data.timestamp.getTime() >
      latestTemperatureData.timestamp.getTime() - timeHorizonMs,
  );

  const margin = { top: 40, right: 30, bottom: 50, left: 40 };
  const { width, height } = bounds;
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;

  const timeDomain = extent(temperatureData, getX) as [Date, Date];
  timeDomain[1] = new Date(
    Math.max(
      timeDomain[0].getTime() + timeHorizonMs - 1000,
      timeDomain[1].getTime(),
    ),
  );
  const xScale = scaleTime<number>({
    domain: timeDomain,
    range: [0, xMax],
  });

  const temperatureDomain = [
    Math.max(0, min(temperatureData, getY)! - 10),
    Math.min(180, max(temperatureData, getY)! + 10),
  ];
  const temperatureYScale = scaleLinear<number>({
    domain: temperatureDomain,
    range: [0, yMax],
    reverse: true,
  });

  return (
    <div className="rounded overflow-hidden shadow-paper max-w-[800px] max-h-[500px] flex flex-1">
      <svg className="bg-stone-400 flex flex-col flex-1 w-full" ref={ref}>
        {bounds && (
          <>
            <Group left={margin.left} top={margin.top}>
              <GridRows
                scale={temperatureYScale}
                width={xMax}
                height={yMax}
                stroke="#cacaca"
              />
              <GridColumns
                scale={xScale}
                width={xMax}
                height={yMax}
                stroke="#cacaca"
              />
              <AxisBottom scale={xScale} top={yMax} />
              <AxisLeft scale={temperatureYScale} />
              <LinePath
                data={temperatureData}
                x={(d) => xScale(getX(d))}
                y={(d) => temperatureYScale(getY(d))}
                stroke="#FA0000"
                strokeWidth={1.5}
                strokeOpacity={1}
              />
            </Group>
          </>
        )}
      </svg>
    </div>
  );
};

export const GaggiaDataView = () => {
  const { telemetryData: temperatureReadings } = useContext(GaggiaDataContext);

  if (temperatureReadings.length < 2) {
    return <SpinnerView text="Waiting for data..." />;
  }
  const latestTemperatureData =
    temperatureReadings[temperatureReadings.length - 1] ?? -1;

  return (
    <div className="w-full flex flex-1 flex-col items-center">
      <TemperatureChart
        temperatureReadings={temperatureReadings}
        timeHorizonMs={60000}
      />
      <p className="w-full text-center text-xl">{`Temperature ${latestTemperatureData.temperature.toLocaleString(
        undefined,
        {
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        },
      )} °C`}</p>
    </div>
  );
};
