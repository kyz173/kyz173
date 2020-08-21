## 0723 camera 합성영상 실행 code 따라가기


1) ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/common/chains_main_linux_iss.c
에 있는 main_iss메뉴 파트의 case '2': 를 따름.
```
case '2':
  gChains_usecaseCfg.displayType = CHAINS_DISPLAY_TYPE_HDMI_1080P;
  chains_issMultiCamIspSgx3DSrv_SgxDisplay(&gChains_usecaseCfg);
  break;
```

1-1) gChains_usecaseCfg 는 header파일인 ~/sdkvision/vision_sdk/apps/src/hlos/adas/include/chains.h 에 정의되어있음 원본은 Chains_Ctrl 구조체
```
typedef struct {
    UInt32 algProcId;
    /**<  Processor ID on which algorithm runs for
     *    - Frame copy algorithm use-case
     *    - DMA SW MS algorithm use-case
     */

    UInt32 numLvdsCh;
    /**< Number of channels of LVDS to enable */

    Chains_DisplayType displayType;
    /**< LCD/HDM display */

    Chains_CaptureSrc captureSrc;
    /**< OV/HDMI-720p/HDMI-1080p capture */

    AlgorithmLink_SrvOutputModes svOutputMode;
    /**< To slect 2D vs 3D Surround View (SRV) Alg */
    UInt32 numPyramids;
    /**< numPyramids - used to select Alg with One/Two Pyramid Mode in  Dense Optical Flow*/
    Bool enableCarOverlayInAlg;
    /**< Set to 1, if DSP need to create the car image, apply only for 2D SRV */

    Bool enableAutoCalib;
    /**< Set to 1, if auto calibration is called to get initial calibration matrix */

    Bool enablePersmatUpdate;
    /**< Set to 1, if initial calibration matrix is updated by Harris corner detection + BRIEF */

    Chains_AutoCalibrationParams calibrationParams;
    /* Advanced Settings for AutoCalibration */

    char sensorName[ISS_SENSORS_MAX_NAME];
    /**< Name of the sensor, used by the ISS usecases */
    IssM2mIspLink_OperatingMode ispOpMode;
    /**< ISP Operation Mode */
} Chains_Ctrl;
```

2) chains_issMultiCamIspSgx3DSrv_SgxDisplay 함수는 ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/usecases/iss_multi_cam_isp_sgx_3d_srv_display 에 정의
```
typedef struct {
    /**< Link Id's and device IDs to use for this use-case */
    chains_issMultiCaptIsp_Sgx3DsrvObj  ucObj;

    UInt32                              numDisLinks;

    Chains_Ctrl                        *chainsCfg;

    Sgx3DsrvLink_UpdateRenderCfgPrms    renderCfgPrms;

    AppCtrl_IssParams                   appCtrlIssPrms;
    UInt32                              numCh;

} Chains_issMultiCaptIsp_Sgx3DsrvAppObj;
```
```
Void chains_issMultiCamIspSgx3DSrv_SgxDisplay(Chains_Ctrl *chainsCfg)
{
    char ch, chPrev;
    UInt32 done = FALSE;
    Bool startWithCalibration;
    Chains_issMultiCaptIsp_Sgx3DsrvAppObj chainsObj;

    chainsObj.chainsCfg = chainsCfg;
    chPrev = '1';

    chainsObj.chainsCfg->numLvdsCh = 4;
    chainsObj.numCh = 4u;

    do
    {
        done = FALSE;
        /* Set startWithCalibration = TRUE to start the demo with calibration.
           Else it will use the previously calibrated LUTs */
        startWithCalibration = TRUE;
        ChainsCommon_SurroundView_CalibInit(
                                    startWithCalibration,
                                    chainsObj.chainsCfg->svOutputMode);

        if(ALGLINK_GALIGN3D_CALMODE_FORCE_USERGASGXLUT != \
          (AlgorithmLink_GAlign3DCalibrationMode)\
                                        ChainsCommon_SurroundView_getCalMode())
        {
            Vps_printf(" CHAINS: -------------------------------------------------------------------- \n");
            Vps_printf(" CHAINS: Calibrated SGX LUT is NOT present \n");
            Vps_printf(" CHAINS: Generate SGX LUT by running the 'Surround View Calibration' use case \n");
            Vps_printf(" CHAINS: -------------------------------------------------------------------- \n");

            ChainsCommon_SurroundView_CalibDeInit();

            return;
        }

        chains_issMultiCaptIsp_Sgx3Dsrv_Create(&chainsObj.ucObj, &chainsObj);

        chains_issMultiCaptIsp_Sgx3Dsrv_StartApp(&chainsObj);

        ChainsCommon_prfLoadCalcEnable(TRUE, FALSE, FALSE);

        while(!done)
        {
            ch = Chains_menu3DSrvRunTime();

            switch(ch)
            {
                case '0':
                    chPrev = ChainsCommon_SurroundView_MenuCalibration();
                    done = TRUE;
                    break;
                case 'p':
                case 'P':
                    ChainsCommon_PrintStatistics();
                    chains_issMultiCaptIsp_Sgx3Dsrv_printStatistics(&chainsObj.ucObj);
                    chains_issMultiCaptIsp_Sgx3Dsrv_printBufferStatistics(&chainsObj.ucObj);
                    break;
                case 'a':
                case 'A':
                case 'b':
                case 'B':
                case 'c':
                case 'C':
                case 'd':
                case 'D':
                case 'g':
                case 'G':
                case 'i':
                case 'I':
                case 'j':
                case 'J':
                case 'k':
                case 'K':
                case 'l':
                case 'L':
                case 'm':
                case 'M':
                case 'n':
                case 'N':
                case 'q':
                case 'Q':
                case 't':
                case 'T':
                case 'v':
                case 'V':
                case 'w':
                case 'W':
                case 'x':
                case 'X':
                case 'y':
                case 'Y':
                case 'z':
                case 'Z':
                case '<':
                case '>':
                case '1':
                case '2':
                case '3':
                    chainsObj.renderCfgPrms.inputChar = ch;
                    System_linkControl(
                        SYSTEM_LINK_ID_SGX3DSRV_0,
                        SYSTEM_COMMON_CMD_UPDATE_RENDER_VIEW,
                        &chainsObj.renderCfgPrms,
                        sizeof(Sgx3DsrvLink_UpdateRenderCfgPrms),
                        TRUE);
                    break;
                default:
                    Vps_printf("\nUnsupported option '%c'. Please try again\n", ch);
                    break;
            }
        }

        chains_issMultiCaptIsp_Sgx3Dsrv_StopApp(&chainsObj);

        ChainsCommon_SurroundView_CalibDeInit();

    } while(chPrev != '3');
}
```

2-1) Chains_menu3DSrvRunTime();
 ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/common/chains_main_linux_settings_vision.c 에 있음.
```
 char Chains_menu3DSrvRunTime()
{
    Vps_printf(gChains_3DSrvRunTimeMenu);

    return Chains_readChar();
}
```
 라고 되어있는데 printf 매개변수는 그냥 메뉴 전체를 뽑는 string임.

2-2) System_linkControl함수 ~/sdkvision/vision_sdk/links_fw/include/link_api/system.h
/**
 *******************************************************************************
 *
 * \brief Send a control command to a link
 *
 *   The link must be created before a control command could be sent.
 *   It need not be in start state for it to be able to received
 *   a control command
 *
 * \param linkId       [IN] link ID for which control command is intended
 * \param cmd          [IN] Link specific command ID
 * \param pPrm         [IN] Link specific command parameters
 * \param prmSize      [IN] Size of the parameter
 * \param waitAck      [IN] TRUE: wait until link ACKs the sent command,
 *                          FALSE: return after sending command
 *
 * \return SYSTEM_LINK_STATUS_SOK on success
 *
 *******************************************************************************
 */
Int32 System_linkControl(UInt32 linkId,
                         UInt32 cmd,
                         Void *pPrm,
                         UInt32 prmSize,
                         Bool waitAck);

2-3) SYSTEM_COMMON_CMD_UPDATE_RENDER_VIEW 이라는 command ID가 들어가는데, 이게 어떤 명령일까? => ~/sdkvision/vision_sdk/apps/src/hlos/modules/sgx3Dsrv/sgx3DsrvLink_tsk.c

~/sdkvision/vision_sdk/links_fw/include/link_api/systemLink_common.h 
```
#define되어있는데 하드웨어 단 예약어이다. ㅜㅜ

case SYSTEM_COMMON_CMD_UPDATE_RENDER_VIEW:
                {
                    Sgx3DsrvLink_UpdateRenderCfgPrms *cfgPrms =
                        (Sgx3DsrvLink_UpdateRenderCfgPrms *) OSA_msgGetPrm(pRunMsg);
                    pObj->renderCfgPrms.inputChar = cfgPrms->inputChar;
                }
                OSA_tskAckOrFreeMsg(pRunMsg, status);
                Sgx3DsrvLink_drvUpdateRenderedView(pObj);
                break;
```
SYSTEM_COMMON_CMD_GET_LOAD ...?

결국 다르게 함.

Void edit_chains_saveDisFrame(char *filename, Chains_Ctrl *chainsCfg)
{
	FILE* input;
	input = fopen(filename,"w");
	fwrite(&chainsCfg->captureSrc, sizeof(int), 100, input); // 100units
	//fprintf(input, "%d", chainsCfg->captureSrc);
	fprintf(input, "\r\n\n");
	//fprintf(input, "%d", chainsCfg->displayType);
	fwrite(&chainsCfg->displayType, sizeof(int), 100, input);
	fclose(input);
}
위 함수를 만들어 chains_main_linux_iss.c에 넣었는데, 잘 될지는 의문이다. 더 아랫단에 넣어놔야할까? 
edit_chains_saveDisFrame("outputfiles.YUV",&gChains_usecaseCfg); 형태로 넣는다.
다음엔 chains_issMultiCaptIsp_Sgx3Dsrv.c 에 넣어보려고 한다.


3) chains_issMultiCaptIsp_Sgx3Dsrv_Create 함수
 chains_issMultiCaptIsp_Sgx3Dsrv_StartApp 함수

~/sdkvision/vision_sdk/apps/src/hlos/infoadas/src/chains/iss_multi_cam_isp_sgx_3d_srv_display/chains_issMultiCaptIsp_Sgx3Dsrv.c 에 위치.

Int32 chains_issMultiCaptIsp_Sgx3Dsrv_CreateApp(struct vivi_sink *sink, struct vivi_source *source)
{
    Int32 status;
    Chains_issMultiCaptIsp_Sgx3DsrvAppObj *pObj
        = (Chains_issMultiCaptIsp_Sgx3DsrvAppObj*)&gIssMultiCaptIsp_Sgx3DsrvObj;
    chains_issMultiCaptIsp_Sgx3DsrvObj *pUcObj = &pObj->ucObj;

    Vps_printf(" CHAIN: chains_issMultiCaptIsp_Sgx3Dsrv_CreateApp !!!\n");

    chains_issMultiCaptIsp_Sgx3Dsrv_InitApp();

#ifndef QNX_BUILD
    pObj->bEglInfoInCreate = sink->bEglInfoInCreate;
#endif

    status = chains_issMultiCaptIsp_Sgx3Dsrv_Create(&gIssMultiCaptIsp_Sgx3DsrvObj.ucObj, &gIssMultiCaptIsp_Sgx3DsrvObj);

    /* Let's set the epLink ids now */
    pUcObj = &gIssMultiCaptIsp_Sgx3DsrvObj.ucObj;
    sink->eplink_id[0] = pUcObj->EpSink_imLinkID;
    sink->eplink_id[1] = pUcObj->EpSink_3dLinkID;

    Vps_printf(" CHAIN: chains_issMultiCaptIsp_Sgx3Dsrv_CreateApp DONE !!!\n");
    return status;
}

Int32 chains_issMultiCaptIsp_Sgx3Dsrv_StartApp()
{
    Int32 status;
    Chains_issMultiCaptIsp_Sgx3DsrvAppObj *pObj
        = (Chains_issMultiCaptIsp_Sgx3DsrvAppObj*)&gIssMultiCaptIsp_Sgx3DsrvObj;

    Vps_printf(" CHAIN: chains_issMultiCaptIsp_Sgx3Dsrv_StartApp !!!\n");

    ChainsCommon_statCollectorReset();
    ChainsCommon_memPrintHeapStatus();

    /* Sets Default ISP/SIMCOP Config from DCC */
    System_linkControl(SYSTEM_LINK_ID_APP_CTRL,
        APP_CTRL_LINK_CMD_ISS_DEFAULT_CONFIG,
        &pObj->appCtrlIssPrms,
        sizeof(pObj->appCtrlIssPrms), TRUE);

    System_linkControl(SYSTEM_LINK_ID_APP_CTRL,
        APP_CTRL_LINK_CMD_SET_BOARD_MUXES,
        &pObj->appCtrlIssPrms.issSensorInfo,
        sizeof(pObj->appCtrlIssPrms.issSensorInfo), TRUE);

    System_linkControl(SYSTEM_LINK_ID_APP_CTRL,
        APP_CTRL_LINK_CMD_ISS_SENSOR_START,
        &pObj->appCtrlIssPrms.issSensorInfo,
        sizeof(pObj->appCtrlIssPrms.issSensorInfo), TRUE);

    status = chains_issMultiCaptIsp_Sgx3Dsrv_Start(&pObj->ucObj);

    ChainsCommon_prfLoadCalcEnable(TRUE, FALSE, FALSE);

    Vps_printf(" CHAIN: chains_issMultiCaptIsp_Sgx3Dsrv_StartApp DONE!!!\n");
    return status;
}
