import React, { PropsWithChildren, useEffect, useState } from 'react';
import io from 'socket.io-client';

const host =
  process.env.NODE_ENV === 'development'
    ? 'http://kahvipi.local'
    : window.location.protocol +
      '//' +
      window.location.hostname +
      ':' +
      window.location.port;

const socket = io(host, {
  transports: ['websocket'],
});

console.log('SocketIO Host: ' + host);
console.log('NODE_ENV: ' + process.env.NODE_ENV);

export interface ITelemetryData {
  timestamp: Date;
  temperature: number;
  setpoint: number;
}

export interface ITelemetry {
  timestamp: number;
  temperature: number;
}

export interface IGaggiaDataContext {
  telemetryData: ITelemetryData[];
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

  const [telemetryData, setTelemetryData] = useState<ITelemetryData[]>([]);

  useEffect(() => {
    socket.on('connect', () => setSocketConnected(true));
    socket.on('disconnect', () => setSocketConnected(false));
    socket.on('telemetry', (data: ITelemetryData) => {
      console.log(
        'Received telemetry: ' + JSON.stringify({ ...data }, undefined, 2),
      );

      setTelemetryData((prev) => {
        return [
          ...prev,
          {
            timestamp: new Date(data.timestamp),
            temperature: data.temperature,
            setpoint: data.setpoint,
          },
        ];
      });
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
        telemetryData: telemetryData,
      }}
    >
      {children}
    </GaggiaDataContext.Provider>
  );
};
