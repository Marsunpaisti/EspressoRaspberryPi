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
  telemetryData,
  timeHorizonMs,
}: {
  telemetryData: ITelemetryData[];
  timeHorizonMs: number;
}) => {
  const [ref, bounds] = useMeasure();

  const latestTemperatureData = telemetryData[telemetryData.length - 1] ?? -1;
  const temperatureData = telemetryData.filter(
    (data) =>
      data.timestamp.getTime() >=
      latestTemperatureData.timestamp.getTime() - timeHorizonMs - 500,
  );

  const xAxisTickValues = [];
  for (let i = timeHorizonMs; i >= 0; i = i - 5000) {
    const offsetTickLocation = new Date(
      latestTemperatureData.timestamp.getTime() - i,
    );
    if (offsetTickLocation >= telemetryData[0].timestamp) {
      xAxisTickValues.push(offsetTickLocation);
    }
  }

  const margin = { top: 40, right: 30, bottom: 50, left: 40 };
  const { width, height } = bounds;
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;

  const timeDomain = extent(temperatureData, getX) as [Date, Date];
  timeDomain[1] = new Date(timeDomain[0].getTime() + timeHorizonMs);

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
                tickValues={xAxisTickValues}
              />
              <AxisLeft scale={temperatureYScale} />
              <AxisBottom
                scale={xScale}
                top={yMax}
                tickValues={xAxisTickValues}
                tickFormat={(d) => {
                  const deltaTime =
                    (d as Date).getTime() -
                    latestTemperatureData.timestamp.getTime();
                  return (deltaTime / 1000).toLocaleString(undefined, {
                    maximumFractionDigits: 1,
                    minimumFractionDigits: 1,
                  });
                }}
              />
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
        telemetryData={temperatureReadings}
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
