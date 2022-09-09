import { GaggiaDataContextProvider } from '../contexts/GaggiaDataContext';
import { GaggiaDataGraph } from './GaggiaDataGraph';

export const App = () => {
  return (
    <GaggiaDataContextProvider>
      <div className="text-2xl font-bold">Hello world!</div>
      <GaggiaDataGraph />
    </GaggiaDataContextProvider>
  );
};
