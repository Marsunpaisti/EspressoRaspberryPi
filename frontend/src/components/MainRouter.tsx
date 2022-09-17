import { GaggiaDataView } from './GaggiaDataView';
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import { Spinner } from './Spinner';
import { useContext } from 'react';
import { GaggiaDataContext } from '../contexts/GaggiaDataContext';

const SpinnerView = () => {
  return (
    <div className="w-full flex-1 flex-col flex justify-center items-center">
      <div className="max-w-[30%] max-h-[30%] aspect-square">
        <div className="w-full h-full max-w-[150px] max-h-[150px] aspect-square">
          <Spinner />
        </div>
      </div>
    </div>
  );
};
export const MainRouter = () => {
  const { socketConnected } = useContext(GaggiaDataContext);

  return (
    <BrowserRouter>
      <div className="flex flex-1 flex-col w-full h-full bg-stone-700">
        <div className="bg-stone-800 w-full py-2 px-2 text-cente shadow-black shadow-sm flex flex-row">
          <h1 className="text-xl font-bold flex flex-row items-center justify-start">
            EspressoPI Control Panel
          </h1>
          <div
            className="flex flex-row flex-1 justify-end"
            style={{
              fontVariationSettings: "'FILL' 1",
            }}
          >
            <Link to="/">
              <div className="h-full flex flex-row justify-center items-center font-bold mx-4">
                <span className="material-symbols-outlined">home</span>
                <span className="hidden sm:block">Home</span>
              </div>
            </Link>
            <Link to="/config">
              <div className="h-full flex flex-row justify-center items-center font-bold mx-4">
                <span className="material-symbols-outlined">settings</span>
                <span className="hidden sm:block">Config</span>
              </div>
            </Link>
          </div>
        </div>
        <div className="flex flex-col flex-1 justify-start items-center py-4 px-2 w-full ">
          {socketConnected && (
            <Routes>
              <Route path="/" element={<GaggiaDataView />} />
              <Route path="/config" element={<div>Config</div>} />
            </Routes>
          )}
          {!socketConnected && <SpinnerView />}
        </div>
      </div>
    </BrowserRouter>
  );
};
