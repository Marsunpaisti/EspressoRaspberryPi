import { useContext } from 'react';
import {
  GaggiaDataContext,
  ITelemetryData,
} from '../contexts/GaggiaDataContext';
import { scaleTime, scaleLinear, scaleOrdinal } from '@visx/scale';
import { extent, max, min } from 'd3-array';
import { Group } from '@visx/group';
import { LinePath } from '@visx/shape';
import { SpinnerView } from './MainRouter';
import { GridRows, GridColumns } from '@visx/grid';
import { AxisLeft, AxisBottom } from '@visx/axis';
import useMeasure from 'react-use-measure';
import { LegendOrdinal, LegendItem, LegendLabel } from '@visx/legend';
import colors from 'tailwindcss/colors';

export interface TelemetryDataWithDeltaTime extends ITelemetryData {
  deltaTime: number;
}

const getDeltaTime = (d: TelemetryDataWithDeltaTime) => d.deltaTime;
const getTemperature = (d: TelemetryDataWithDeltaTime) => d.temperature;
const getSetpoint = (d: TelemetryDataWithDeltaTime) => d.setpoint;

const ordinalColorScale = scaleOrdinal({
  domain: ['Temperature', 'Setpoint'],
  range: [colors.red[500], colors.blue[500]],
});

const TemperatureChart = ({
  telemetryData,
  timeHorizonSeconds,
}: {
  telemetryData: ITelemetryData[];
  timeHorizonSeconds: number;
}) => {
  const [ref, bounds] = useMeasure();

  const latestTemperatureData = telemetryData[telemetryData.length - 1] ?? -1;
  const temperatureData = telemetryData
    .map<TelemetryDataWithDeltaTime>((td) => {
      return {
        ...td,
        deltaTime:
          td.timestamp.getTime() - latestTemperatureData.timestamp.getTime(),
      };
    })
    .filter((td) => Math.ceil(td.deltaTime / 1000) >= -timeHorizonSeconds);

  const xAxisTickValues = [];
  for (let i = -timeHorizonSeconds; i <= 0; i = i + 5) {
    xAxisTickValues.push(i * 1000);
  }
  const margin = { top: 0, right: 15, bottom: 30, left: 30 };
  const { width, height } = bounds;
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;

  const timeDomain = extent(temperatureData, getDeltaTime) as [number, number];
  const xScale = scaleTime<number>({
    domain: timeDomain,
    range: [0, xMax],
  });

  const lowestTemperature = min(temperatureData, getTemperature)!;
  const highestTemperature = max(temperatureData, getTemperature)!;
  const temperatureDomain = [
    Math.max(0, Math.min(lowestTemperature - 5, 50)),
    Math.min(180, Math.max(highestTemperature + 5, 100)),
  ];
  const temperatureYScale = scaleLinear<number>({
    domain: temperatureDomain,
    range: [0, yMax],
    reverse: true,
  });

  return (
    <div className="relative rounded overflow-hidden shadow-paper max-w-[800px] max-h-[500px] flex flex-1 flex-col bg-stone-400 ">
      <LegendOrdinal scale={ordinalColorScale}>
        {(labels) => (
          <div className="top-6 left-10 flex flex-row gap-3 px-[35px] ">
            {labels.map((label, i) => (
              <LegendItem key={`legend-quantile-${i}`}>
                <svg width={15} height={15}>
                  <rect fill={label.value} width={15} height={15} />
                </svg>
                <LegendLabel align="left" margin="0 0 0 4px">
                  {label.text}
                </LegendLabel>
              </LegendItem>
            ))}
          </div>
        )}
      </LegendOrdinal>
      <svg className="flex flex-col flex-1 w-full overflow-visible" ref={ref}>
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
              <LinePath
                data={temperatureData}
                x={(d) => xScale(getDeltaTime(d))}
                y={(d) => temperatureYScale(getTemperature(d))}
                className="stroke-red-500"
                strokeWidth={1.5}
                strokeOpacity={1}
              />
              <LinePath
                data={temperatureData}
                x={(d) => xScale(getDeltaTime(d))}
                y={(d) => temperatureYScale(getSetpoint(d))}
                className="stroke-blue-500"
                strokeWidth={0.5}
                strokeOpacity={1}
              />
              <AxisLeft left={-1} scale={temperatureYScale} />
              <AxisBottom
                left={-1}
                scale={xScale}
                top={yMax}
                tickFormat={(d) => {
                  return `T-${((d as number) / 1000).toLocaleString(undefined, {
                    maximumFractionDigits: 1,
                    minimumFractionDigits: 0,
                  })}`;
                }}
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
        timeHorizonSeconds={60}
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
