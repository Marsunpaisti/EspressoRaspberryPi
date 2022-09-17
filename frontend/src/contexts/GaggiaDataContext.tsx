import React, { PropsWithChildren, useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io({
  transports: ['websocket'],
});

export interface TemperatureReading {
  timestamp: Date;
  temperature: number;
}
export interface SetpointReading {
  timestamp: Date;
  setpoint: number;
}

export interface ITelemetry {
  temperature: number;
  setpoint: number;
}

export interface IGaggiaDataContext {
  temperatureReadings: TemperatureReading[];
  setpointReadings: SetpointReading[];
  brewTimer?: number;
  socketConnected: boolean;
}

export const GaggiaDataContext = React.createContext<IGaggiaDataContext>(
  {} as IGaggiaDataContext,
);

export const GaggiaDataContextProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const [socketConnected, setSocketConnected] = useState(false);

  const [temperatureReadings, setTemperatureReadings] = useState<
    TemperatureReading[]
  >([]);

  const [setpointReadings, setSetpointReadings] = useState<SetpointReading[]>(
    [],
  );

  useEffect(() => {
    socket.on('connect', () => setSocketConnected(true));
    socket.on('disconnect', () => setSocketConnected(false));
    socket.on('telemetry', (data: ITelemetry) => {
      console.log('Received telemetry: ' + data);
      const ts = new Date();

      if (data.setpoint != undefined) {
        setSetpointReadings((prev) => {
          return [
            ...prev,
            {
              timestamp: ts,
              setpoint: data.setpoint,
            },
          ];
        });
      }

      if (data.temperature != undefined) {
        setTemperatureReadings((prev) => {
          return [
            ...prev,
            {
              timestamp: ts,
              temperature: data.temperature,
            },
          ];
        });
      }
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('telemetry');
    };
  }, []);

  return (
    <GaggiaDataContext.Provider
      value={{
        socketConnected,
        temperatureReadings,
        setpointReadings,
      }}
    >
      {children}
    </GaggiaDataContext.Provider>
  );
};
