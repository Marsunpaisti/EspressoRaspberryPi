import { GaggiaDataView } from './GaggiaDataView';
import { BrowserRouter, Link, Route, Routes, useMatch } from 'react-router-dom';
import { Spinner } from './Spinner';
import {
  PropsWithChildren,
  ReactNode,
  useContext,
  useState,
  useEffect,
} from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';
import { GaggiaConfigView } from './GaggiaConfigView';
import coffeeIcon from '../assets/coffee.png';

export const SpinnerView = ({ text }: { text: string }) => {
  return (
    <div className="absolute m-auto left-0 right-0 top-0 bottom-0 w-full flex-1 flex-col flex justify-center items-center pointer-events-none">
      <div className="max-w-[50%] max-h-[50%] aspect-square">
        <div className="relative w-full h-full max-w-[250px] max-h-[250px] aspect-square">
          <Spinner />
          <p className="absolute m-auto left-4 right-4 top-4 bottom-4 text-center flex items-center justify-center text-blue-100 text-sm">
            {text}
          </p>
        </div>
      </div>
    </div>
  );
};

const NavLink = ({
  to,
  children,
}: {
  to: string;
  children: ReactNode | ReactNode[] | undefined;
}) => {
  const matchesPath = useMatch(to);
  return (
    <Link to={to}>
      <div
        className={`h-full flex flex-row justify-center items-center font-bold mx-4 select-none transition-all duration-150 ${
          matchesPath ? 'text-blue-300 scale-125' : ''
        }`}
      >
        {children}
      </div>
    </Link>
  );
};

export const FadeIn: React.FC<PropsWithChildren> = ({ children }) => {
  const [fadedIn, setFadedIn] = useState(false);

  useEffect(() => {
    setFadedIn(true);
  }, [setFadedIn]);
  return (
    <div
      className={`flex flex-1 flex-col w-full h-full transition-opacity duration-200 ${
        fadedIn ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {children}
    </div>
  );
};

export const MainRouter = () => {
  const { socketConnected } = useContext(GaggiaDataContext);

  return (
    <BrowserRouter>
      <div className="flex flex-1 flex-col w-full h-full">
        <div className="bg-stone-800 w-full py-1 px-2 text-cente shadow-paper flex flex-row border-b-2 border-b-stone-800">
          <h1 className="text-xl font-bold flex flex-row items-center justify-start">
            <img
              src={coffeeIcon}
              className="max-h-[36px] mr-1 w-auto object-contain"
            />
            EspressoPI Controller
          </h1>
          <div
            className="flex flex-row flex-1 justify-end"
            style={{
              fontVariationSettings: "'FILL' 1",
            }}
          >
            <NavLink to="/">
              <span className="material-symbols-outlined">monitoring</span>
              <span className="hidden sm:block">Monitor</span>
            </NavLink>
            <NavLink to="/config">
              <span className="material-symbols-outlined">settings</span>
              <span className="hidden sm:block">Configure</span>
            </NavLink>
          </div>
        </div>
        <div className="flex flex-col flex-1 py-2 px-2 w-full justify-center items-center">
          {socketConnected && (
            <Routes>
              <Route
                path="/"
                element={
                  <FadeIn key="/">
                    <GaggiaDataView />
                  </FadeIn>
                }
              />
              <Route
                path="/config"
                element={
                  <FadeIn key="/config">
                    <GaggiaConfigView />
                  </FadeIn>
                }
              />
            </Routes>
          )}
          {!socketConnected && <SpinnerView text="Connecting..." />}
        </div>
      </div>
    </BrowserRouter>
  );
};
