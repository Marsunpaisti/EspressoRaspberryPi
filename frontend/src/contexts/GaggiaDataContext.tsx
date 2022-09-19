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

export interface ITelemetryData {
  timestamp: Date;
  temperature: number;
  setpoint: number;
  shotDuration: number;
}

export interface ITelemetryMessage {
  ts: number;
  temp: number;
  set: number;
  shotdur: number;
}

export interface IGaggiaConfig {
  shotTimeLimit: number;
  steamSetpoint: number;
  brewSetpoint: number;
}

export interface IGaggiaDataContext {
  telemetryData: ITelemetryData[];
  brewTimer?: number;
  socketConnected: boolean;
  gaggiaConfig: IGaggiaConfig;
  setShotTimeLimit: (limit: number) => void;
  setBrewSetpoint: (setpoint: number) => void;
  setSteamSetpoint: (setpoint: number) => void;
}

export const GaggiaDataContext = React.createContext<IGaggiaDataContext>(
  {} as IGaggiaDataContext,
);

const convertTelemetryMsgToData = (msg: ITelemetryMessage): ITelemetryData => {
  return {
    timestamp: new Date(msg.ts),
    temperature: msg.temp,
    setpoint: msg.set,
    shotDuration: msg.shotdur,
  };
};

export const GaggiaDataContextProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const [socketConnected, setSocketConnected] = useState(false);
  const [telemetryData, setTelemetryData] = useState<ITelemetryData[]>([]);
  const [gaggiaConfig, setGaggiaConfig] = useState<IGaggiaConfig>({
    brewSetpoint: -1,
    steamSetpoint: -1,
    shotTimeLimit: -1,
  });
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

  const setSteamSetpoint = useCallback((setpoint: number) => {
    socket.emit('set_steam_setpoint', setpoint);
  }, []);

  const setBrewSetpoint = useCallback((setpoint: number) => {
    socket.emit('set_brew_setpoint', setpoint);
  }, []);

  const setShotTimeLimit = useCallback((limit: number) => {
    socket.emit('set_shot_time_limit', limit);
  }, []);

  useEffect(() => {
    socket.on('connect', () => setSocketConnected(true));
    socket.on('disconnect', () => setSocketConnected(false));
    socket.on('telemetry', (msg: ITelemetryMessage) => {
      registerNewTelemetry(msg);
    });

    socket.on('telemetryHistory', (msgs: ITelemetryMessage[]) => {
      registerTelemetryHistory(msgs);
    });
    socket.on('config', (msg: IGaggiaConfig) => {
      setGaggiaConfig(msg);
    });

    if (socket.connected) {
      setSocketConnected(true);
    }
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('telemetryHistory');
      socket.off('config');
      socket.off('telemetry');
    };
  }, [registerNewTelemetry, registerTelemetryHistory]);

  return (
    <GaggiaDataContext.Provider
      value={{
        socketConnected,
        telemetryData,
        gaggiaConfig,
        setShotTimeLimit,
        setBrewSetpoint,
        setSteamSetpoint,
      }}
    >
      {children}
    </GaggiaDataContext.Provider>
  );
};
