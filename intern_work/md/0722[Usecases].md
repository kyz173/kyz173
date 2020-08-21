##0722 : sdk와 usecase 운용

### preview1 사용이전에 확인할 사항
중요한 점 : MAKECONFIG = tda2px_evm_linux_all 옵션을 사용하기 때문에 linux기반 A15 위에서 작동하게 된다.
=> rtos의 자료는 사용할 수 없고 hlos를 봐야한다.

RTOS (Real Time Operating System)
HLOS (high level Operating System)

```
<설치경로>/vision_sdk/apps/src/hlos/adas/src/usecases/
```
안에 있는 usecase를 보고 수정하도록 하자

### preview2 기타 각종파일들의 위치
> sdk실행시 main 파트 : ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/common/
 main파트 : chains_main.c
 main_iss메뉴 파트 : common/chains_main_linux_iss.c

+ usecase들의 모음 : 
> ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/usecases
>> + iss 4중 이미지 합성 :
 iss_multi_cam_isp_sgx_2mp_3d_srv
>> + iss 이미지캡쳐 :
 iss_capture_isp_display
  (그 외에도 iss~라는 이름으로 시작하는 애들 모두.. iss_multi_cam_isp_sgx_2mp_3d_srv_adaptive, iss_multi_cam_isp_sgx_3d_srv_display)
>> + calibration :
 srv_calibration

+ usecase중 iss 4개카메라 띄우는 함수 :
> Void chains_issMultiCamIspSgx3DSrv_SgxDisplay(Chains_Ctrl *chainsCfg)
 chains_main_linux_iss.c 에서는 매개변수로 얘를 넣는다 : &gChains_usecaseCfg

+ gChain구조체의 선언위치와
> ~/sdkvision/vision_sdk/apps/src/hlos/adas/include/chains.h

+ 그리고 그 함수의 정의 위치
> ~/sdkvision/vision_sdk/apps/src/hlos/adas/src/usecases/iss_multi_cam_isp_sgx_3d_srv_display/chains_issMultiCaptIsp_Sgx3Dsrv.c


### preview3 Chain 구조체 파라미터 확인
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
---
### 1. new usecase 제작

1) 다른 usecase를 참고하여 txt 를 하나 만든다. single camera를 위한 display일 때 이렇게 작성된다.

```
Usecase : chains_vipSingleCam_Display

Capture -> Display_Video
GrpxSrc -> Display_Grpx

```

이들은 사전의 정의된 이름이 정해져 있는 것으로 판단된다. 이름을 이상하게 바꾸지 말자.


2) 이렇게 정해주면, 
```
<설치경로>/vision_sdk/apps/tools/vision_sdk_usecase_gen/bin/vsdk_linux.out
```
vsdk_linux.out 이라는 tool을 이용해 priv header와 source code를 제작할 수 있다.

```
./vsdk_linux.out -file <설치경로>/vision_sdk/apps/src/hlos/adas/src/usecases/
<새로만든usecase_folder>/<새로만든usecase>.txt ./<코드out시킬경로>
```

이렇게 하면 priv.c와 priv.h라는 파일들이 생성될텐데, 이들을 이용하여 c파일을 제작해주면 된다.

+ -img 라는 옵션도 있던데 어떻게 쓰는지는 잘 모르겠다. -help로 모든 옵션을 검토할 수 있다.

### 2. new usecase 빌드추가

1) 새로만든 usecase가 있는 폴더에 MAKEFILE.MK를 추가시킨다. 보통 이 파일은 아무다른 usecase에 있는 MAKEFILE.MK을 들고오면 된다. (빌드시에 다른 환경에서 MAKE해줄 이유가 없다면)

2) cfg.mk 파일을 생성한다
 2가지의 할 일이 있는데, 알고리즘 플러그인을 사용한다면 ALG plugin 폴더이름을 가져와서 yes로 세팅하면 되고
 이 usecase를 사용할 때 계산을 활성화 시킬 cpu를 할당하는 일이다.
 IPU1_0, IPU1_1, IPU2, DSP1, DSP2, EVE1, EVE2, EVE3, EVE4, A15_0 중에서 선택할 수 있으며, 필요한 cpu의 활성화를 위해서는 다음과 같이 입력해두면 된다.
 NEED_PROC_IPU1_0 = yes

3) main config 수정
 ```
 <설치경로>/vision_sdk/$(MAKEAPPNAME)/configs/cfg.mk 라고 설명되어있다.

 다시말하면,
 <설치경로>/vision_sdk/apps/configs/cfg.mk
 ```
 새로 추가된 usecase를 build할수 있도록 variable을 추가해준다.

 나에게 맞는 LIST에 넣어주면되는데 
 ```
 LINUX_TDA2XX_UC_LIST = \
 UC_avbrx_dec_display \
 ...
 UC_my_usecase ★
 ```
 이렇게 하면 된다. (별표는 새로추가한 내 usecase)

4) build config 수정
 ```
 <설치경로>/vision_sdk/$(MAKEAPPNAME)/configs/$(MAKECONFIG)/uc_cfg.mk 라고 설명되어있다.

 다시말하면,
 <설치경로>/vision_sdk/apps/configs/tda2px_evm_linux_all/uc_cfg.mk
 ```
 을 보면, 3)에서 선언해두었던 variable을 프로그램빌드시에 여기서 flag를 만들어 보내는 역할을 해준다. 새로만든 flag를 yes로 해둔다.
 >UC_my_usecase = yes

5) build과정중에 usecase들어왔는지 확인법

 make showconfig를 해주면, 내가 생성한 usecase가 있는지 확인이 가능하다.
 #Use-cases include in build, 확인
 같은방법으로 algorithm도 확인가능
 #Alg plugins included in build

 + 이거 확인하는게 정말 중요한게, 빌드상의 옵션을 제대로 파악해야 어플리케이션을 만들려고 했을때 발생할 문제를 방지할 수 있다. ex) showconfig 로 확인했는데, CPU include가 no일 때 (PROC_IPU1_0_INCLUDE = no) 2)에서처럼 해당 cpu를 사용하고자 하는 어플리케이션을 선언해둔 경우 작동이 안될 수도 있음.

6) main에서 실행해서 디버깅
 문서의 최상단에서 설명했던 chains_main.c 같은 파일에서 
 ```
 #ifdef UC_my_usecase
  MY_usecase_run(&gChains_usecaseCfg);
 #endif 
 "\r\n "
 ```
 과 같은 테스트도 가능하다. => 테스트 까지는 성공!
 
 함수를 어떤식으로 불러오는지는 확인이 여전히 필요한 상태

---

### 실수하던 점
 + usecase를 만들거나 수정하고 나서 다시 make -s -j depend 와 make -s -j로 만들어주고 실행하기는 하는데, 그러고나면 rootfs의 apps.out이 바뀔 것이고, 이게 ti_components/os_tools/linux/targetfs로 옮겨지는데, 이걸 다시 압축하여 vision_sdk/binaries/apps/tda2px_evm_linux_all/hlos/linux/boot 여기에 옮겨놔야 sd card 포팅이 될 것이다.

 + LENS.BIN이나 CALMAT.BIN등의 파일들의 위치를 잘 확인하자. 안 넣기도 하더라 나.
  => 특히 calmat이 없으면 ISS 싱글카메라만 실행되고 나머지는 Unsupported option이라는 디폴트 메세지가 출력된다.


### 앞으로 할 일

1-1) rtos에 정의되어있는 saveDisFrame 소스를 hlos단으로 가져와 빌드에 성공시키고, 해당 c파일내에 정의된 함수를 include해서 사용한다
1-2) 아니면 null 포인터를 하나 만들어서 display로 가기전에 한 번, 버퍼로 사용하여 이미지를 저장시킨다.

