import { useContext, useEffect, useRef, useState } from 'react';
import {
  GaggiaDataContext,
  TemperatureReading,
} from '../contexts/GaggiaDataContext';
import { scaleTime, scaleLinear } from '@visx/scale';
import { extent, max, min } from 'd3-array';
import { Group } from '@visx/group';
import { LinePath } from '@visx/shape';
import { SpinnerView } from './MainRouter';
import { GridRows, GridColumns } from '@visx/grid';
import { AxisLeft, AxisBottom } from '@visx/axis';

const getX = (d: TemperatureReading) => d.timestamp;
const getY = (d: TemperatureReading) => d.temperature;
const TemperatureChart = ({
  temperatureReadings,
  timeHorizonMs,
}: {
  temperatureReadings: TemperatureReading[];
  timeHorizonMs: number;
}) => {
  const svgRef = useRef<SVGSVGElement | null>();
  const [svgBounds, setSvgBounds] = useState<undefined | DOMRect>(undefined);

  useEffect(() => {
    setSvgBounds(svgRef.current?.getBoundingClientRect());
  }, [svgRef]);

  const latestTemperatureData =
    temperatureReadings[temperatureReadings.length - 1] ?? -1;
  const temperatureData = temperatureReadings.filter(
    (data) =>
      data.timestamp.getTime() >
      latestTemperatureData.timestamp.getTime() - timeHorizonMs,
  );

  const gridTickRowValues = [];
  for (let i = 0; i <= 50; i++) {
    gridTickRowValues.push(i * 5);
  }
  const timeDomain = extent(temperatureData, getX) as [Date, Date];
  timeDomain[1] = new Date(
    Math.max(
      timeDomain[0].getTime() + timeHorizonMs - 1000,
      timeDomain[1].getTime(),
    ),
  );
  const xScale = scaleTime<number>({
    domain: timeDomain,
    range: [0, svgBounds?.width ?? 0],
  });

  const temperatureDomain = [
    Math.max(20, min(temperatureData, getY)! - 20),
    Math.min(170, max(temperatureData, getY)! + 20),
  ];
  const temperatureYScale = scaleLinear<number>({
    domain: temperatureDomain,
    range: [svgBounds?.height ?? 0, 0],
  });

  console.log('XRange: ' + xScale.range());
  console.log('YRange: ' + temperatureYScale.range());

  return (
    <div className="rounded overflow-hidden shadow-paper max-w-[800px] max-h-[500px] flex flex-1">
      <svg
        className="bg-stone-400 flex flex-col flex-1 w-full"
        ref={(r) => (svgRef.current = r)}
      >
        {svgRef.current && svgBounds && (
          <>
            <GridRows
              scale={temperatureYScale}
              width={svgBounds!.width}
              height={svgBounds!.height}
              stroke="#CACACA"
              tickValues={gridTickRowValues}
            />
            <Group left={0} top={0}>
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
  const { temperatureReadings } = useContext(GaggiaDataContext);

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
