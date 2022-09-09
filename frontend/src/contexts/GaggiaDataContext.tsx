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
      console.log(data);
      const ts = new Date();
      setSetpointReadings((prev) => {
        return [
          ...prev,
          {
            timestamp: ts,
            setpoint: data.setpoint,
          },
        ];
      });
      setTemperatureReadings((prev) => {
        return [
          ...prev,
          {
            timestamp: ts,
            temperature: data.temperature,
          },
        ];
      });
    });
    setInterval(() => {
      if (socket.connected) {
        socket.emit('test_print', Date.now().toString(), (response: any) => {
          console.log('test_print response: ' + response);
        });
      }
    }, 3000);

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
