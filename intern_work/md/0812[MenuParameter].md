### Menu Parameter 처리

메뉴에서 display 이미지를 컨트롤하기 위한 파라미터

### 메뉴

1. 결론부터 말하자면, chainsObj.renderCfgPrms.inputChar = ch; 에서 keyboard interrupt buffer에서부터 데이터를 받아
Sgx3DsrvLink_UpdateRenderCfgPrms 로 선언된 renderCfgPrms 는 inputChar밖에 없는 구조체로 넘겨준다.

2. 1의 chainsObj는 Chains_issMultiCaptIsp_Sgx3DsrvAppObj로 선언되어있는데, 이는

Struct type | class name
------------ | ------------- 
chains_issMultiCaptIsp_Sgx3DsrvObj | ucObj;
UInt32                            |  numDisLinks;
Chains_Ctrl                       | *chainsCfg;
Sgx3DsrvLink_UpdateRenderCfgPrms  |  renderCfgPrms;
AppCtrl_IssParams                 |  appCtrlIssPrms;
UInt32                            |  numCh;
chains_issMultiCaptIsp_Sgx3DsrvObj|  ucObj;
UInt32                            |  numDisLinks;
Chains_Ctrl                       | *chainsCfg;
Sgx3DsrvLink_UpdateRenderCfgPrms  |  renderCfgPrms;
AppCtrl_IssParams                 |  appCtrlIssPrms;
UInt32                            |  numCh;
로 구성되어있다.


3. 이하 관련 코드 첨부.

> <설치폴더>/vision_sdk/apps/src/hlos/adas/include/chains.h
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

> <설치폴더>/vision_sdk/links_fw/include/link_api/sgx3DsrvLink.h
```
typedef struct {
    char     inputChar;
    /**< Input character to update the render configuration */
} Sgx3DsrvLink_UpdateRenderCfgPrms;
```

> <설치폴더>/vision_sdk/apps/src/hlos/adas/src/usecases/iss_multi_cam_isp_sgx_3d_srv_display/chains_issMultiCaptIsp_Sgx3Dsrv.c
chains_issMultiCamIspSgx3DSrv_SgxDisplay 
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
    Chains_issMultiCaptIsp_Sgx3DsrvAppObj chainsObj; <<<< 중요한 녀석 >>>>

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

### 실제 MenuParamenter가 적용되는 곳

> <설치폴더>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/render.cpp

1. render_process_keys(char input) 에서 아까 받은 파라미터가 반영된다.
 srv_viewports[current_viewport].animate 로 애니메이션 유무를 확인하고 (시점 휙휙변하는 그것)
 전역변수 flaot x y z 와 delta로 데이터를 저장해
 함수의 마지막에 render_updateView()를 호출해서 반영한다.

이하 코드 중 일부
```
void render_process_keys(char input){
        switch(input)
	{
	case 'c':
		MODE_CAM(srv_coords_vp[current_viewport]);
		break;
	case 't':
		MODE_TARGET(srv_coords_vp[current_viewport]);
		break;
	case 'a':
		MODE_ANGLE(srv_coords_vp[current_viewport]);
		break;
	case 'b':
		srv_param_bowl = !srv_param_bowl;
		break;
	.... 이하 생략
        }
        render_updateView();

        ... 생략
}

```

2. viewports
num_viewports = sizeof(srv_viewports)/sizeof(srv_viewport_t);
라는 부분이 있는데, 코드 최상단에 보면 
```
srv_viewport_t srv_viewports[] = {
	{
		x : 0,
		y : 0,
		width : 960,
		height: 1080,
		animate: true,
	},
	{
		x : 960,
		y : 0,
		width : 960,
		height: 1080,
		animate: false,
	}
};
```
의 형태로 이루어져 있어서 animating을 넣을 것인지, 보는 위치는 어느 곳을 디폴트로 넣을 것인지, resoultion은 어떻게 넣을 것인지 설정해줄수 있는데, 이를 여러개 설정할 수록 rendering이 많아지게 된다. default는 현재처럼 단 두 개.


3. render_updateView() 
glm(OpenGL matrix)의 mat4 를 사용하며
i는 2)에서 가져온 viewport라고 할 때,
 mProjection[i] : perspective matrix 설정
 mView[i] : Camera 위치 설정 ( defalut는 4,3,3 이다. )
 rotate함수를 사용하여 기존 mView[i]를 anglex angley anglez 값에따라 회전시키고
 mModel_bowl[i] : vec3 데이터를 mat4데이터로 scaling (변환 -> bowl이미지를 만들기위한 전초작업)
 mMVP_bowl[i] : mProjection[i] * mView[i] * mModel_bowl[i]; (변환)
 car_updateView(i) 로 연결된다.

4. car_updateView(i)
> <설치폴더>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/car.cpp

해당파일로 넘어오면 car_updateView(int i)가 있는데, 자세히보면 그냥 준비되어있는 car rendering을 3)에서 이미지가 회전된만큼 같은 비율로 돌려서 넣을 뿐이다. (하단코드참조)
```
void car_updateView(int i)
{
	glm::mat4 mView_car;
	mView_car = glm::scale(mView[i], glm::vec3(car_data[active_car_index].scale));
	mView_car = glm::rotate(mView_car, degreesToRadians(car_data[active_car_index].xrot_degrees), glm::vec3(1.0, 0.0, 0.0));
	mView_car = glm::rotate(mView_car, degreesToRadians(car_data[active_car_index].yrot_degrees), glm::vec3(0.0, 1.0, 0.0));
	mView_car = glm::rotate(mView_car, degreesToRadians(car_data[active_car_index].zrot_degrees), glm::vec3(0.0, 0.0, 1.0));
	mMVP_car[i] = mProjection[i] * mView_car;
}
```

5. mMVP_bowl[i]는 OpenGl에서...
> <설치폴더>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/srv.cpp

srv.cpp 에 mMVP_bowl[]를 extern으로 선언해주어서, render.h를 include 하는 것으로 해당 전역변수를 여기서도 사용할 수 있도록 하였다.

여기서부터는 OpenGL의 공부가 필요하다.
onscreen_mesh_state_restore_program_textures_attribs() 라는 함수를 찾아보면, 내부에 다음과 같은 OpenGL메소드가 있다.
```
glUniformMatrix4fv(mvMatrixLocation, 1, GL_FALSE, &mMVP_bowl[viewport_id][0][0]);
```
먼저, glUniformMatrix4fv 함수는 다음과 같은 구성을 가지고 있다.

```
void glUniformMatrix4fv(GLint location,
 	                GLsizei count,
 	                GLboolean transpose,
 	                const GLfloat *value);
```
 의미 | 변수명
------------ | ------------- 
저장할 데이터의 Uniform | mvMatrixLocation
실데이터를 받을 버퍼 | &mMVP_bowl[viewport_id][0][0]







