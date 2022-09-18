import React, {
  PropsWithChildren,
  useCallback,
  useEffect,
  useState,
} from 'react';
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
  reconnectionDelayMax: 3000,
});

console.log('SocketIO Host: ' + host);
console.log('NODE_ENV: ' + process.env.NODE_ENV);

export interface ITelemetryData {
  timestamp: Date;
  temperature: number;
  setpoint: number;
  dutyCycle: number;
}

export interface ITelemetryMessage {
  ts: number;
  temp: number;
  out: number;
  set: number;
}

export interface IGaggiaDataContext {
  telemetryData: ITelemetryData[];
  brewTimer?: number;
  socketConnected: boolean;
}

export const GaggiaDataContext = React.createContext<IGaggiaDataContext>(
  {} as IGaggiaDataContext,
);

const convertTelemetryMsgToData = (msg: ITelemetryMessage): ITelemetryData => {
  return {
    timestamp: new Date(msg.ts),
    temperature: msg.temp,
    setpoint: msg.set,
    dutyCycle: msg.out,
  };
};

export const GaggiaDataContextProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const [socketConnected, setSocketConnected] = useState(false);
  const [telemetryData, setTelemetryData] = useState<ITelemetryData[]>([]);
  const MAX_STORED_DATAPOINTS = 180;

  const registerNewTelemetry = useCallback(
    (msg: ITelemetryMessage) => {
      setTelemetryData((prev) => {
        if (!prev.find((p) => p.timestamp.getTime() === msg.ts)) {
          const newData = [...prev, convertTelemetryMsgToData(msg)];
          if (newData.length > MAX_STORED_DATAPOINTS)
            return newData.slice(-MAX_STORED_DATAPOINTS);
          return newData;
        } else {
          return prev;
        }
      });
    },
    [setTelemetryData],
  );

  const registerTelemetryHistory = useCallback(
    (msgs: ITelemetryMessage[]) => {
      setTelemetryData((prev) => {
        const filtered = msgs.filter(
          (d) => !prev.find((p) => p.timestamp.getTime() === d.ts),
        );
        const converted = filtered.map((d) => convertTelemetryMsgToData(d));
        const newData = [...prev, ...converted];
        if (newData.length > MAX_STORED_DATAPOINTS)
          return newData.slice(-MAX_STORED_DATAPOINTS);
        return newData;
      });
    },
    [setTelemetryData],
  );

  useEffect(() => {
    socket.on('connect', () => setSocketConnected(true));
    socket.on('disconnect', () => setSocketConnected(false));
    socket.on('telemetry', (msg: ITelemetryMessage) => {
      console.log(
        'Received telemetry: ' + JSON.stringify({ ...msg }, undefined, 2),
      );
      registerNewTelemetry(msg);
    });

    socket.on('telemetryHistory', (msgs: ITelemetryMessage[]) => {
      console.log('Received telemetry history with length: ' + msgs.length);
      registerTelemetryHistory(msgs);
    });

    if (socket.connected) {
      setSocketConnected(true);
    }
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('telemetry');
    };
  }, [registerNewTelemetry, registerTelemetryHistory]);

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
