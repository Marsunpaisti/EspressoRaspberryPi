/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: PIDController.h
 *
 * Code generated for Simulink model 'PIDController'.
 *
 * Model version                  : 1.2
 * Simulink Coder version         : 9.6 (R2021b) 14-May-2021
 * C/C++ source code generated on : Thu Sep  8 18:36:29 2022
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#ifndef RTW_HEADER_PIDController_h_
#define RTW_HEADER_PIDController_h_
#include <math.h>
#include <string.h>
#ifndef PIDController_COMMON_INCLUDES_
#define PIDController_COMMON_INCLUDES_
#include "rtwtypes.h"
#endif                                 /* PIDController_COMMON_INCLUDES_ */

#include "PIDController_types.h"
#include "rt_defines.h"

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

/* Block states (default storage) for system '<Root>' */
typedef struct {
  real_T Integrator_DSTATE;            /* '<S36>/Integrator' */
  real_T Filter_DSTATE;                /* '<S31>/Filter' */
  uint8_T Integrator_IC_LOADING;       /* '<S36>/Integrator' */
  uint8_T Filter_IC_LOADING;           /* '<S31>/Filter' */
} DW_PIDController_T;

/* Real-time Model Data Structure */
struct tag_RTM_PIDController_T {
  const char_T * volatile errorStatus;
  DW_PIDController_T *dwork;
};

/* Model entry point functions */
extern void PIDController_initialize(RT_MODEL_PIDController_T *const
  PIDController_M, real_T *PIDController_U_u, real_T *PIDController_U_P, real_T *
  PIDController_U_I, real_T *PIDController_U_D, real_T *PIDController_U_N,
  real_T *PIDController_U_I0, real_T *PIDController_U_D0, real_T
  *PIDController_U_UpperLimit, real_T *PIDController_U_LowerLimit, real_T
  *PIDController_U_extTs, real_T *PIDController_Y_y);
extern void PIDController_step(RT_MODEL_PIDController_T *const PIDController_M,
  real_T PIDController_U_u, real_T PIDController_U_P, real_T PIDController_U_I,
  real_T PIDController_U_D, real_T PIDController_U_N, real_T PIDController_U_I0,
  real_T PIDController_U_D0, real_T PIDController_U_UpperLimit, real_T
  PIDController_U_LowerLimit, real_T PIDController_U_extTs, real_T
  *PIDController_Y_y);
extern void PIDController_terminate(RT_MODEL_PIDController_T *const
  PIDController_M);

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S44>/Data Type Duplicate' : Unused code path elimination
 * Block '<S44>/Data Type Propagation' : Unused code path elimination
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Note that this particular code originates from a subsystem build,
 * and has its own system numbers different from the parent model.
 * Refer to the system hierarchy for this subsystem below, and use the
 * MATLAB hilite_system command to trace the generated code back
 * to the parent model.  For example,
 *
 * hilite_system('pid_codegen/PIDController')    - opens subsystem pid_codegen/PIDController
 * hilite_system('pid_codegen/PIDController/Kp') - opens and selects block Kp
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'pid_codegen'
 * '<S1>'   : 'pid_codegen/PIDController'
 * '<S2>'   : 'pid_codegen/PIDController/Anti-windup'
 * '<S3>'   : 'pid_codegen/PIDController/D Gain'
 * '<S4>'   : 'pid_codegen/PIDController/Filter'
 * '<S5>'   : 'pid_codegen/PIDController/Filter ICs'
 * '<S6>'   : 'pid_codegen/PIDController/I Gain'
 * '<S7>'   : 'pid_codegen/PIDController/Ideal P Gain'
 * '<S8>'   : 'pid_codegen/PIDController/Ideal P Gain Fdbk'
 * '<S9>'   : 'pid_codegen/PIDController/Integrator'
 * '<S10>'  : 'pid_codegen/PIDController/Integrator ICs'
 * '<S11>'  : 'pid_codegen/PIDController/N Copy'
 * '<S12>'  : 'pid_codegen/PIDController/N Gain'
 * '<S13>'  : 'pid_codegen/PIDController/P Copy'
 * '<S14>'  : 'pid_codegen/PIDController/Parallel P Gain'
 * '<S15>'  : 'pid_codegen/PIDController/Reset Signal'
 * '<S16>'  : 'pid_codegen/PIDController/Saturation'
 * '<S17>'  : 'pid_codegen/PIDController/Saturation Fdbk'
 * '<S18>'  : 'pid_codegen/PIDController/Sum'
 * '<S19>'  : 'pid_codegen/PIDController/Sum Fdbk'
 * '<S20>'  : 'pid_codegen/PIDController/Tracking Mode'
 * '<S21>'  : 'pid_codegen/PIDController/Tracking Mode Sum'
 * '<S22>'  : 'pid_codegen/PIDController/Tsamp - Integral'
 * '<S23>'  : 'pid_codegen/PIDController/Tsamp - Ngain'
 * '<S24>'  : 'pid_codegen/PIDController/postSat Signal'
 * '<S25>'  : 'pid_codegen/PIDController/preSat Signal'
 * '<S26>'  : 'pid_codegen/PIDController/Anti-windup/Disc. Clamping Parallel'
 * '<S27>'  : 'pid_codegen/PIDController/Anti-windup/Disc. Clamping Parallel/Dead Zone'
 * '<S28>'  : 'pid_codegen/PIDController/Anti-windup/Disc. Clamping Parallel/Dead Zone/External'
 * '<S29>'  : 'pid_codegen/PIDController/Anti-windup/Disc. Clamping Parallel/Dead Zone/External/Dead Zone Dynamic'
 * '<S30>'  : 'pid_codegen/PIDController/D Gain/External Parameters'
 * '<S31>'  : 'pid_codegen/PIDController/Filter/Disc. Forward Euler Filter'
 * '<S32>'  : 'pid_codegen/PIDController/Filter ICs/External IC'
 * '<S33>'  : 'pid_codegen/PIDController/I Gain/External Parameters'
 * '<S34>'  : 'pid_codegen/PIDController/Ideal P Gain/Passthrough'
 * '<S35>'  : 'pid_codegen/PIDController/Ideal P Gain Fdbk/Disabled'
 * '<S36>'  : 'pid_codegen/PIDController/Integrator/Discrete'
 * '<S37>'  : 'pid_codegen/PIDController/Integrator ICs/External IC'
 * '<S38>'  : 'pid_codegen/PIDController/N Copy/Disabled'
 * '<S39>'  : 'pid_codegen/PIDController/N Gain/External Parameters'
 * '<S40>'  : 'pid_codegen/PIDController/P Copy/Disabled'
 * '<S41>'  : 'pid_codegen/PIDController/Parallel P Gain/External Parameters'
 * '<S42>'  : 'pid_codegen/PIDController/Reset Signal/Disabled'
 * '<S43>'  : 'pid_codegen/PIDController/Saturation/External'
 * '<S44>'  : 'pid_codegen/PIDController/Saturation/External/Saturation Dynamic'
 * '<S45>'  : 'pid_codegen/PIDController/Saturation Fdbk/Disabled'
 * '<S46>'  : 'pid_codegen/PIDController/Sum/Sum_PID'
 * '<S47>'  : 'pid_codegen/PIDController/Sum Fdbk/Disabled'
 * '<S48>'  : 'pid_codegen/PIDController/Tracking Mode/Disabled'
 * '<S49>'  : 'pid_codegen/PIDController/Tracking Mode Sum/Passthrough'
 * '<S50>'  : 'pid_codegen/PIDController/Tsamp - Integral/External Ts'
 * '<S51>'  : 'pid_codegen/PIDController/Tsamp - Ngain/External Ts'
 * '<S52>'  : 'pid_codegen/PIDController/postSat Signal/Forward_Path'
 * '<S53>'  : 'pid_codegen/PIDController/preSat Signal/Forward_Path'
 */
#endif                                 /* RTW_HEADER_PIDController_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
