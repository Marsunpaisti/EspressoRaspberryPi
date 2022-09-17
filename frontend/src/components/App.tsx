import { GaggiaDataContextProvider } from '../contexts/GaggiaDataContext';
import { MainRouter } from './MainRouter';

export const App = () => {
  return (
    <GaggiaDataContextProvider>
      <MainRouter />
    </GaggiaDataContextProvider>
  );
};
