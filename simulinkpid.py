from ctypes import *
import os.path

dll_name = "DiscretePid.so"
dllabspath = os.path.dirname(
    os.path.abspath(__file__)) + os.path.sep + dll_name
libc = CDLL(dllabspath)

# Rename main functions for readability
cPID_Initialize = libc.PIDController_initialize
cPID_Step = libc.PIDController_step

# Create both ctypes structures of both state variables


class DW_PIDController_T(Structure):
    _fields_ = [("Integrator_DSTATE", c_double),
                ("Filter_DSTATE", c_double),
                ("Integrator_IC_LOADING", c_uint8),
                ("Filter_IC_LOADING", c_uint8)]


class RT_MODEL_PIDController_T(Structure):
    _fields_ = [("errorStatus", c_char_p),
                ("dwork", POINTER(DW_PIDController_T))]


class DiscretePid():
    def __init__(self, pGain: float, iGain: float, dGain: float, filterCoeff: float, upperLimit: float, lowerLimit: float) -> None:
        self.DW_PIDController_T = DW_PIDController_T()
        self.RT_MODEL_PIDController_T = RT_MODEL_PIDController_T()
        self.RT_MODEL_PIDController_T.dwork = pointer(self.DW_PIDController_T)
        self.ptr_RT_MODEL_PIDController_T = pointer(
            self.RT_MODEL_PIDController_T)
        self.error = c_double()
        self.pGain = c_double()
        self.iGain = c_double()
        self.dGain = c_double()
        self.filterCoeff = c_double()
        self.integratorState = c_double()
        self.filterState = c_double()
        self.upperLimit = c_double()
        self.lowerLimit = c_double()
        self.sampleTime = c_double()
        self.output = c_double()
        self.ptr_output = pointer(self.output)

        cPID_Initialize(self.ptr_RT_MODEL_PIDController_T, byref(self.error), byref(self.pGain), byref(self.iGain), byref(self.dGain), byref(self.filterCoeff), byref(
            self.integratorState), byref(self.filterState), byref(self.upperLimit), byref(self.lowerLimit), byref(self.sampleTime), self.ptr_output)
        print("INITIALIZE")

        print(
            f"RT_MODEL_PIDController_T.FILTER: {self.RT_MODEL_PIDController_T.dwork.contents.Filter_DSTATE}")
        print(
            f"RT_MODEL_PIDController_T.INTEGRATOR: {self.RT_MODEL_PIDController_T.dwork.contents.Integrator_DSTATE}")
        self.setGains(pGain, iGain, dGain, filterCoeff, upperLimit, lowerLimit)

    def setGains(self, pGain: float, iGain: float, dGain: float, filterCoeff: float, upperLimit: float, lowerLimit: float):
        self.pGain.value = pGain
        self.iGain.value = iGain
        self.dGain.value = dGain
        self.filterCoeff.value = filterCoeff
        self.upperLimit.value = upperLimit
        self.lowerLimit.value = lowerLimit

    def getOutput(self):
        return self.output.value

    def step(self, error: float, sampleTime: float) -> float:
        self.error.value = error
        self.sampleTime.value = sampleTime
        print("BEFORE")
        print(
            f"DW_PIDController_T.FILTER: {self.DW_PIDController_T.Filter_DSTATE}")
        print(
            f"DW_PIDController_T.INTEGRATOR: {self.DW_PIDController_T.Integrator_DSTATE}")
        print(
            f"RT_MODEL_PIDController_T.FILTER: {self.RT_MODEL_PIDController_T.dwork.contents.Filter_DSTATE}")
        print(
            f"RT_MODEL_PIDController_T.INTEGRATOR: {self.RT_MODEL_PIDController_T.dwork.contents.Integrator_DSTATE}")
        print(
            f"SELF.FILTER: {self.filterState}")
        print(
            f"SELF.INTEGRATOR: {self.integratorState}")

        print(f"Calling PID with err: {self.error}, p: {self.pGain}, i: {self.iGain}, d: {self.dGain}, N: {self.filterCoeff}, iState: {self.integratorState}, fState: {self.filterState}, upperLimit: {self.upperLimit} , lowerLimit: {self.lowerLimit}, Ts: {self.sampleTime}")
        cPID_Step(self.ptr_RT_MODEL_PIDController_T, self.error, self.pGain, self.iGain, self.dGain, self.filterCoeff,
                  self.integratorState, self.filterState, self.upperLimit, self.lowerLimit, self.sampleTime, self.ptr_output)
        print("AFTER")
        print(
            f"DW_PIDController_T.FILTER: {self.DW_PIDController_T.Filter_DSTATE}")
        print(
            f"DW_PIDController_T.INTEGRATOR: {self.DW_PIDController_T.Integrator_DSTATE}")
        print(
            f"RT_MODEL_PIDController_T.FILTER: {self.RT_MODEL_PIDController_T.dwork.contents.Filter_DSTATE}")
        print(
            f"RT_MODEL_PIDController_T.INTEGRATOR: {self.RT_MODEL_PIDController_T.dwork.contents.Integrator_DSTATE}")
        print(
            f"SELF.FILTER: {self.filterState}")
        print(
            f"SELF.INTEGRATOR: {self.integratorState}")
        print(f"Out: {self.output}")
        self.filterState.value = self.RT_MODEL_PIDController_T.dwork.contents.Filter_DSTATE
        self.integratorState.value = self.RT_MODEL_PIDController_T.dwork.contents.Integrator_DSTATE
        return self.output.value
