/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: PIDController.c
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

#include "PIDController.h"
#include "PIDController_private.h"

/* Model step function */
void PIDController_step(RT_MODEL_PIDController_T *const PIDController_M, real_T
  PIDController_U_u, real_T PIDController_U_P, real_T PIDController_U_I, real_T
  PIDController_U_D, real_T PIDController_U_N, real_T PIDController_U_I0, real_T
  PIDController_U_D0, real_T PIDController_U_UpperLimit, real_T
  PIDController_U_LowerLimit, real_T PIDController_U_extTs, real_T
  *PIDController_Y_y)
{
  DW_PIDController_T *PIDController_DW = PIDController_M->dwork;
  real_T rtb_NProdOut;
  real_T rtb_Sum;
  real_T rtb_Switch_k;
  real_T rtb_Switch_l;
  boolean_T rtb_NotEqual;

  /* DiscreteIntegrator: '<S36>/Integrator' incorporates:
   *  Inport: '<Root>/I0'
   */
  if (PIDController_DW->Integrator_IC_LOADING != 0) {
    PIDController_DW->Integrator_DSTATE = PIDController_U_I0;
  }

  /* DiscreteIntegrator: '<S31>/Filter' incorporates:
   *  Inport: '<Root>/D0'
   */
  if (PIDController_DW->Filter_IC_LOADING != 0) {
    PIDController_DW->Filter_DSTATE = PIDController_U_D0;
  }

  /* Product: '<S39>/NProd Out' incorporates:
   *  DiscreteIntegrator: '<S31>/Filter'
   *  Inport: '<Root>/D'
   *  Inport: '<Root>/N'
   *  Inport: '<Root>/u'
   *  Product: '<S30>/DProd Out'
   *  Sum: '<S31>/SumD'
   */
  rtb_NProdOut = (PIDController_U_u * PIDController_U_D -
                  PIDController_DW->Filter_DSTATE) * PIDController_U_N;

  /* Sum: '<S46>/Sum' incorporates:
   *  DiscreteIntegrator: '<S36>/Integrator'
   *  Inport: '<Root>/P'
   *  Inport: '<Root>/u'
   *  Product: '<S41>/PProd Out'
   */
  rtb_Sum = (PIDController_U_u * PIDController_U_P +
             PIDController_DW->Integrator_DSTATE) + rtb_NProdOut;

  /* Switch: '<S44>/Switch2' incorporates:
   *  Inport: '<Root>/LowerLimit'
   *  Inport: '<Root>/UpperLimit'
   *  RelationalOperator: '<S44>/LowerRelop1'
   *  RelationalOperator: '<S44>/UpperRelop'
   *  Switch: '<S44>/Switch'
   */
  if (rtb_Sum > PIDController_U_UpperLimit) {
    /* Outport: '<Root>/y' */
    *PIDController_Y_y = PIDController_U_UpperLimit;
  } else if (rtb_Sum < PIDController_U_LowerLimit) {
    /* Switch: '<S44>/Switch' incorporates:
     *  Inport: '<Root>/LowerLimit'
     *  Outport: '<Root>/y'
     */
    *PIDController_Y_y = PIDController_U_LowerLimit;
  } else {
    /* Outport: '<Root>/y' incorporates:
     *  Switch: '<S44>/Switch'
     */
    *PIDController_Y_y = rtb_Sum;
  }

  /* End of Switch: '<S44>/Switch2' */

  /* Switch: '<S29>/Switch' incorporates:
   *  Inport: '<Root>/LowerLimit'
   *  Inport: '<Root>/UpperLimit'
   *  RelationalOperator: '<S29>/u_GTE_up'
   *  RelationalOperator: '<S29>/u_GT_lo'
   *  Switch: '<S29>/Switch1'
   */
  if (rtb_Sum >= PIDController_U_UpperLimit) {
    rtb_Switch_k = PIDController_U_UpperLimit;
  } else if (rtb_Sum > PIDController_U_LowerLimit) {
    /* Switch: '<S29>/Switch1' */
    rtb_Switch_k = rtb_Sum;
  } else {
    rtb_Switch_k = PIDController_U_LowerLimit;
  }

  /* End of Switch: '<S29>/Switch' */

  /* Sum: '<S29>/Diff' */
  rtb_Switch_k = rtb_Sum - rtb_Switch_k;

  /* RelationalOperator: '<S26>/NotEqual' incorporates:
   *  Gain: '<S26>/ZeroGain'
   */
  rtb_NotEqual = (0.0 != rtb_Switch_k);

  /* Signum: '<S26>/SignPreSat' */
  if (rtb_Switch_k < 0.0) {
    rtb_Sum = -1.0;
  } else if (rtb_Switch_k > 0.0) {
    rtb_Sum = 1.0;
  } else {
    rtb_Sum = rtb_Switch_k;
  }

  /* End of Signum: '<S26>/SignPreSat' */

  /* Product: '<S33>/IProd Out' incorporates:
   *  Inport: '<Root>/I'
   *  Inport: '<Root>/u'
   */
  rtb_Switch_k = PIDController_U_u * PIDController_U_I;

  /* Update for DiscreteIntegrator: '<S36>/Integrator' */
  PIDController_DW->Integrator_IC_LOADING = 0U;

  /* DataTypeConversion: '<S26>/DataTypeConv1' */
  rtb_Sum = fmod(rtb_Sum, 256.0);

  /* Signum: '<S26>/SignPreIntegrator' */
  if (rtb_Switch_k < 0.0) {
    rtb_Switch_l = -1.0;
  } else if (rtb_Switch_k > 0.0) {
    rtb_Switch_l = 1.0;
  } else {
    rtb_Switch_l = rtb_Switch_k;
  }

  /* End of Signum: '<S26>/SignPreIntegrator' */

  /* DataTypeConversion: '<S26>/DataTypeConv2' */
  rtb_Switch_l = fmod(rtb_Switch_l, 256.0);

  /* Switch: '<S26>/Switch' incorporates:
   *  Constant: '<S26>/Constant1'
   *  DataTypeConversion: '<S26>/DataTypeConv1'
   *  DataTypeConversion: '<S26>/DataTypeConv2'
   *  Logic: '<S26>/AND3'
   *  RelationalOperator: '<S26>/Equal1'
   */
  if (rtb_NotEqual && ((rtb_Sum < 0.0 ? (int32_T)(int8_T)-(int8_T)(uint8_T)
                        -rtb_Sum : (int32_T)(int8_T)(uint8_T)rtb_Sum) ==
                       (rtb_Switch_l < 0.0 ? (int32_T)(int8_T)-(int8_T)(uint8_T)
                        -rtb_Switch_l : (int32_T)(int8_T)(uint8_T)rtb_Switch_l)))
  {
    rtb_Switch_k = 0.0;
  }

  /* End of Switch: '<S26>/Switch' */

  /* Update for DiscreteIntegrator: '<S36>/Integrator' incorporates:
   *  Inport: '<Root>/extTs'
   *  Product: '<S50>/Uintegral*Ts Prod Out'
   */
  PIDController_DW->Integrator_DSTATE += rtb_Switch_k * PIDController_U_extTs;

  /* Update for DiscreteIntegrator: '<S31>/Filter' incorporates:
   *  Inport: '<Root>/extTs'
   *  Product: '<S51>/Ungain*Ts Prod Out'
   */
  PIDController_DW->Filter_IC_LOADING = 0U;
  PIDController_DW->Filter_DSTATE += rtb_NProdOut * PIDController_U_extTs;
}

/* Model initialize function */
void PIDController_initialize(RT_MODEL_PIDController_T *const PIDController_M,
  real_T *PIDController_U_u, real_T *PIDController_U_P, real_T
  *PIDController_U_I, real_T *PIDController_U_D, real_T *PIDController_U_N,
  real_T *PIDController_U_I0, real_T *PIDController_U_D0, real_T
  *PIDController_U_UpperLimit, real_T *PIDController_U_LowerLimit, real_T
  *PIDController_U_extTs, real_T *PIDController_Y_y)
{
  DW_PIDController_T *PIDController_DW = PIDController_M->dwork;

  /* Registration code */

  /* states (dwork) */
  (void) memset((void *)PIDController_DW, 0,
                sizeof(DW_PIDController_T));

  /* external inputs */
  *PIDController_U_u = 0.0;
  *PIDController_U_P = 0.0;
  *PIDController_U_I = 0.0;
  *PIDController_U_D = 0.0;
  *PIDController_U_N = 0.0;
  *PIDController_U_I0 = 0.0;
  *PIDController_U_D0 = 0.0;
  *PIDController_U_UpperLimit = 0.0;
  *PIDController_U_LowerLimit = 0.0;
  *PIDController_U_extTs = 0.0;

  /* external outputs */
  *PIDController_Y_y = 0.0;

  /* InitializeConditions for DiscreteIntegrator: '<S36>/Integrator' */
  PIDController_DW->Integrator_IC_LOADING = 1U;

  /* InitializeConditions for DiscreteIntegrator: '<S31>/Filter' */
  PIDController_DW->Filter_IC_LOADING = 1U;
}

/* Model terminate function */
void PIDController_terminate(RT_MODEL_PIDController_T *const PIDController_M)
{
  /* (no terminate code required) */
  UNUSED_PARAMETER(PIDController_M);
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
