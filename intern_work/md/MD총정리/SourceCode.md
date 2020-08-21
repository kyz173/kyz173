### Ti SDK SourceCode analysis (1)

#### 각종파일들의 위치와 관계 :wrench: 수정중

* sdk 실행시 최상위 메뉴 main
`<설치경로>/vision_sdk/apps/src/hlos/adas/src/common/chains_main.c`
  * main &rarr; iss menu (5번 메뉴)
  `common/chains_main_linux_iss.c`
</br>

* usecase들의 경로
  `<설치경로>/vision_sdk/apps/src/hlos/adas/src/usecases`
  * iss 이미지캡쳐 (1번 메뉴 등):
  `usecases/iss_capture_isp_display`
  * iss 이미지 합성 (2번이나 4번 메뉴 등)
  `usecases/iss_multi_cam_isp_sgx_2mp_3d_srv`
  `usecases/iss_multi_cam_isp_sgx_2mp_3d_srv_adaptive`
  `usecases/iss_multi_cam_isp_sgx_3d_srv_display`
  * calibaration (3번 메뉴):
  `usecases/srv_calibration`

<img src="./pictures/menu_usecase_diagram.png" width="400px" alt="">

---

#### Main & Camera link

* Chains_Ctrl 구조체
`<설치경로>/vision_sdk/apps/src/hlos/adas/include/chains.h`
카메라 input setting과 display단을 연결시켜 줄 때 파라미터나 버퍼등을 넘겨주는 구조체이다

<details>
<summary><span style="color:green">📝Click to expand code "Chains_Ctrl"</span></summary>

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

</details>

&nbsp;
* Display 함수에서의 Chains_Ctrl의 사용
다음 코드는 `chains_main_linux_iss.c` 의 main에 있는 코드의 일부 
`Chains_Ctrl gChains_usecaseCfg;` 로 선언되어, 현재 저장되어있는 파라미터를 `usecase/iss_multi_cam_isp_sgx_3d_srv_display` 안에 있는 함수로 넘겨주는 모습이다.
```
case '2':
  gChains_usecaseCfg.displayType = CHAINS_DISPLAY_TYPE_HDMI_1080P;
  chains_issMultiCamIspSgx3DSrv_SgxDisplay(&gChains_usecaseCfg);
  break;
``` 

&nbsp;
* SgxDisplay 함수
Chains_menu3DSrvRunTime() 이라는 함수에서, 터미널로부터 받아온 keyboard interrupt 를 ch 에 저장하고, 이를 renderCfgPrms에 준다. 이후 System_linkControl 함수가 기존 렌더링에 keyboard interrupt 옵션에 따라 update를 진행할 수 있도록 파라미터들을 rendering 관련 함수부로 넘겨주게 된다.

<details>
<summary><span style="color:green">📝Click to expand code "SgxDisplay"</span></summary>

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

`chainsObj.renderCfgPrms.inputChar = ch;` 에서 keyboard interrupt buffer에서부터 데이터를 받아 `Sgx3DsrvLink_UpdateRenderCfgPrms` 로 선언된 `renderCfgPrms`라는 `inputChar`밖에 없는 구조체로 넘겨주고 있다.

</details>

SYSTEM_LINK_ID_SGX3DSRV_0 와 SYSTEM_COMMON_CMD_UPDATE_RENDER_VIEW 는 하드웨어 단 예약어로, 다른 코드에서 flag로서 작용하도록 해준다.
(#define 0xC105 << 이런식으로 선언되어있음)

---

#### Main Menu & Keyboard interrupt

1. 상단의 SgxDisplay Source code내의 `chains_issMultiCamIspSgx3DSrv_SgxDisplay()`함수의 `chainsObj.renderCfgPrms.inputChar = ch;` 에서 keyboard interrupt buffer에서부터 데이터를 받아 `Sgx3DsrvLink_UpdateRenderCfgPrms` 로 선언된 `renderCfgPrms`라는 `inputChar`밖에 없는 구조체로 넘겨준다.

</br>

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

---

#### 실제 MenuParamenter가 적용되는 곳

> <설치폴더>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/render.cpp

1. render_process_keys(char input) 에서 아까 받은 파라미터가 반영된다.
    srv_viewports[current_viewport].animate 로 애니메이션 유무를 확인하고 (세팅해둔 시점으로 지정된 시간마다 이동)
    전역변수 <span style="color:blue">float</span> x y z 와 delta로 데이터를 저장해
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

</br>

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
</br>

3. render_updateView() 

    glm(OpenGL matrix)의 mat4 를 사용하며
    i는 2에서 가져온 viewport라고 할 때,

    variable/function name | explane
    ------------ | ------------- 
    mProjection[i] | perspective matrix 설정
    mView[i]       |  Camera의 절대 위치 설정 ( default는 4,3,3 이다. )
    rotate()       | mView[i]를 anglex angley anglez 값에 따라 회전
    mModel_bowl[i] |  vec3 데이터를 mat4데이터로 scaling(변환), bowl이미지를 만들기위한 전초작업
    mMVP_bowl[i]   |  mProjection[i] * mView[i] * mModel_bowl[i]; (변환)

    이후 car_updateView(i) 로 연결된다.
</br>

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
</br>

5. mMVP_bowl[i]는 OpenGl에서 처리
> <설치폴더>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/srv.cpp

srv.cpp 에 mMVP_bowl[]를 extern으로 선언해주어서, render.h를 include 하는 것으로 해당 전역변수를 여기서도 사용할 수 있도록 했다.

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



