import { useContext } from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';
import { DataCard } from './GaggiaDataView';

export const GaggiaConfigView = () => {
  const { gaggiaConfig } = useContext(GaggiaDataContext);
  return (
    <div className="flex flex-col items-center">
      <h1>Config</h1>
      <div className="flex flex-col max-w-[300px] gap-2 text-xl">
        <DataCard>
          <div className="w-full flex flex-col items-center">
            <p>Steaming temperature</p>
            <p>{gaggiaConfig.steamSetpoint}</p>
          </div>
        </DataCard>
        <DataCard>
          <div className="w-full flex flex-col items-center">
            <p>Brewing temperature</p>
            <p>{gaggiaConfig.brewSetpoint}</p>
          </div>
        </DataCard>
        <DataCard>
          <div className="w-full flex flex-col items-center">
            <p>Shot time limit</p>
            <p>{gaggiaConfig.shotTimeLimit}</p>
          </div>
        </DataCard>
      </div>
    </div>
  );
};
