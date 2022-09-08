/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: ert_main.c
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

#include <stddef.h>
#include <stdio.h>            /* This example main program uses printf/fflush */
#include "PIDController.h"             /* Model's header file */

static RT_MODEL_PIDController_T PIDController_M_;
static RT_MODEL_PIDController_T *const PIDController_MPtr = &PIDController_M_;/* Real-time model */
static DW_PIDController_T PIDController_DW;/* Observable states */

/* '<Root>/u' */
static real_T PIDController_U_u;

/* '<Root>/P' */
static real_T PIDController_U_P;

/* '<Root>/I' */
static real_T PIDController_U_I;

/* '<Root>/D' */
static real_T PIDController_U_D;

/* '<Root>/N' */
static real_T PIDController_U_N;

/* '<Root>/I0' */
static real_T PIDController_U_I0;

/* '<Root>/D0' */
static real_T PIDController_U_D0;

/* '<Root>/UpperLimit' */
static real_T PIDController_U_UpperLimit;

/* '<Root>/LowerLimit' */
static real_T PIDController_U_LowerLimit;

/* '<Root>/extTs' */
static real_T PIDController_U_extTs;

/* '<Root>/y' */
static real_T PIDController_Y_y;

/*
 * Associating rt_OneStep with a real-time clock or interrupt service routine
 * is what makes the generated code "real-time".  The function rt_OneStep is
 * always associated with the base rate of the model.  Subrates are managed
 * by the base rate from inside the generated code.  Enabling/disabling
 * interrupts and floating point context switches are target specific.  This
 * example code indicates where these should take place relative to executing
 * the generated code step function.  Overrun behavior should be tailored to
 * your application needs.  This example simply sets an error status in the
 * real-time model and returns from rt_OneStep.
 */
void rt_OneStep(RT_MODEL_PIDController_T *const PIDController_M);
void rt_OneStep(RT_MODEL_PIDController_T *const PIDController_M)
{
  static boolean_T OverrunFlag = false;

  /* Disable interrupts here */

  /* Check for overrun */
  if (OverrunFlag) {
    rtmSetErrorStatus(PIDController_M, "Overrun");
    return;
  }

  OverrunFlag = true;

  /* Save FPU context here (if necessary) */
  /* Re-enable timer or interrupt here */
  /* Set model inputs here */

  /* Step the model */
  PIDController_step(PIDController_M, PIDController_U_u, PIDController_U_P,
                     PIDController_U_I, PIDController_U_D, PIDController_U_N,
                     PIDController_U_I0, PIDController_U_D0,
                     PIDController_U_UpperLimit, PIDController_U_LowerLimit,
                     PIDController_U_extTs, &PIDController_Y_y);

  /* Get model outputs here */

  /* Indicate task complete */
  OverrunFlag = false;

  /* Disable interrupts here */
  /* Restore FPU context here (if necessary) */
  /* Enable interrupts here */
}

/*
 * The example "main" function illustrates what is required by your
 * application code to initialize, execute, and terminate the generated code.
 * Attaching rt_OneStep to a real-time clock is target specific.  This example
 * illustrates how you do this relative to initializing the model.
 */
int_T main(int_T argc, const char *argv[])
{
  RT_MODEL_PIDController_T *const PIDController_M = PIDController_MPtr;

  /* Unused arguments */
  (void)(argc);
  (void)(argv);

  /* Pack model data into RTM */
  PIDController_M->dwork = &PIDController_DW;

  /* Initialize model */
  PIDController_initialize(PIDController_M, &PIDController_U_u,
    &PIDController_U_P, &PIDController_U_I, &PIDController_U_D,
    &PIDController_U_N, &PIDController_U_I0, &PIDController_U_D0,
    &PIDController_U_UpperLimit, &PIDController_U_LowerLimit,
    &PIDController_U_extTs, &PIDController_Y_y);

  /* Attach rt_OneStep to a timer or interrupt service routine with
   * period 0.2 seconds (the model's base sample time) here.  The
   * call syntax for rt_OneStep is
   *
   *  rt_OneStep(PIDController_M);
   */
  printf("Warning: The simulation will run forever. "
         "Generated ERT main won't simulate model step behavior. "
         "To change this behavior select the 'MAT-file logging' option.\n");
  fflush((NULL));
  while (rtmGetErrorStatus(PIDController_M) == (NULL)) {
    /*  Perform application tasks here */
  }

  /* Disable rt_OneStep here */
  /* Terminate model */
  PIDController_terminate(PIDController_M);
  return 0;
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
