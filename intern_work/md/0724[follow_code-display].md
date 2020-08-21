## 0724 display 단 변수 확인하기

Calibration된 이미지가 최종적으로 나올때, 나오는 로그는 다음과 같음

```
DISPLAY: Start in progress !!!
DISPLAY: Start Done !!!
SGX3DSRV Link: Start in progress !!!
SGX3DSRV Link: Start Done !!!
ISSCAPTURE: Start in progress !!!
ISSCAPTURE: Start Done !!!
Setting BspUtils_enableUb960CsiOutput!!!!
<이후 메뉴리스트와 함께 영상이 나온다.>
```

각 부분이 어디서 나오나 봤더니 다음과 같다.

+ /links_fw/src/rtos/links_ipu/display/displayLink_drv.c
/apps/src/rtos/modules/display_multi_pipe/displayMultiPipe_drv.c
 -> 얘들은 rtos에서 작동하는데 어떻게..?

+ /apps/src/rtos/modules/sgx3Dsrv/sgx3DsrvLink_drv.c

+ /links_fw/src/rtos/links_ipu/iss_capture/issCaptureLink_drv.c
 -> 얘도 rtos환경이다. 어떻게 굴러가는거길래?

+ /apps/src/rtos/common/chains_main_linux.c
 -> 얘도 rtos

```
Int32 DisplayLink_drvStart(DisplayLink_Obj *pObj)
{
    Int32 status = SYSTEM_LINK_STATUS_SOK;

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" DISPLAY: Start in progress !!!\n");
#endif

    pObj->isDisplayRunning = TRUE;

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" DISPLAY: Start Done !!!\n");
#endif

    return status;
}
```
```
Int32 DisplayMpLink_drvStart(DisplayMpLink_Obj *pObj)
{
    Int32 status = SYSTEM_LINK_STATUS_SOK;

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" DISPLAY: Start in progress !!!\n");
#endif

    pObj->isDisplayRunning = TRUE;

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" DISPLAY: Start Done !!!\n");
#endif

    return status;
}
```
```
Int32 Sgx3DsrvLink_drvStart(Sgx3DsrvLink_Obj *pObj)
{
    Int32 status = SYSTEM_LINK_STATUS_SOK;

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" SGX3DSRV Link: Start in progress !!!\n");
#endif

#ifdef SYSTEM_DEBUG_DISPLAY
    Vps_printf(" SGX3DSRV Link: Start Done !!!\n");
#endif

    return status;
}
```
```
Int32 IssCaptureLink_drvStart(IssCaptureLink_Obj *pObj)
{
    Int32         status;

#ifdef SYSTEM_DEBUG_CAPTURE
    Vps_printf(" ISSCAPTURE: Start in progress !!!\n");
#endif

    status = Fvid2_start(pObj->drvHandle, NULL);
    if (FVID2_SOK != status)
    {
        Vps_printf(" ISSCAPTURE: ERROR: FVID2 Start Failed !!!\n");
        status = SYSTEM_LINK_STATUS_EFAIL;
    }
    else
    {
        pObj->statsStartTime = Utils_getCurGlobalTimeInMsec();

#ifdef SYSTEM_DEBUG_CAPTURE
        Vps_printf(" ISSCAPTURE: Start Done !!!\n");
#endif
        status = SYSTEM_LINK_STATUS_SOK;
    }

    return status;
}
```
```
...
        case APP_CTRL_LINK_CMD_ENABLE_CSI_OUTPUT:
            Vps_printf("Setting BspUtils_enableUb960CsiOutput!!!!\n");
            BspUtils_enableUb960CsiOutput();
...
```

###코드분석시작

1. boot -> links_fw/src/hlos/system/system_common.c
System_init(void) 함수로 시작한다.
<br />
2. 각종 메모리 세팅과 OSA_assert, System ipc 초기화와 link 초기화, wait app 초기화 등을 한다.
 -> System_initLinks 에서 A15를 위한 system link가 시작됨.
 Sgx3DsrvLink_init() 이 surround view를 위한 init을 시작함
 --> apps/src/hlos/modules/sgx3Dsrv/sgx3DsrvLink_tsk.c 으로 연결
<br />
3. Sgx3DsrvLink_init() 은 OSA_tskCreate에서 매개변수로 Sgx3DsrvLink_tskMain 콜백 함수를 사용함.
 -> Sgx3DsrvLink_tskMain() 내부에 OSA_msgGetCmd(pMsg)라고, 터미널 명령을 받아서 안으로 들이고, SYSTEM_CMD_START라는 예약어와 같다면(#define)
 --> Sgx3DsrvLink_drvStart(pObj) 가 실행되면서 터미널에는 Vps_printf(" SGX3DSRV Link: Start in progress !!!\n"); 출력
<br />
4. 그럼 여기서 pObj는 어디서 얻는가? Int32 Sgx3DsrvLink_tskMain(struct OSA_TskHndl *pTsk,
                                    OSA_MsgHndl *pMsg, UInt32 curState)
 함수를 살펴보면 OSA (아마도 여기가 메인 OS terminal이 아닌가 싶다.) 에서부터 메세지 핸들러 *pMsg를 가져온다. 아마도 터미널 메세지를 return해주는 것으로 추정.
 구조체 포인터변수 Sgx3DsrvLink_Obj *pObj = (Sgx3DsrvLink_Obj *) pTsk->appData; 으로 선언하고
 status = Sgx3DsrvLink_drvCreate(pObj, OSA_msgGetPrm(pMsg)); 로 터미널 메세지를 전달해주면서 srv 이미지가 생성되게 된다.
<br />
5. Int32 Sgx3DsrvLink_drvCreate(Sgx3DsrvLink_Obj *pObj,
                             Sgx3DsrvLink_CreateParams *pPrm)
 대망의 srv 이미지 생성부. 같은 sgx3Dsrv 폴더에 있다. sgx3DsrvLink_drv.c

    1. memcpy(&pObj->createArgs, pPrm, sizeof(*pPrm)); 로 터미널 메세지를 받아주고
    2. OSA_assert(pPrm->numInQue <= SGX3DSRV_LINK_IPQID_MAXIPQ); 로 Queue 수량 체크
    3. 이하 for문에서 모든 Queue를 돌며 memcpy 해서 inQueInfo[inQue], inTskInfo[inQue] 두 개의 stack에 채워넣는 형태. (근데 이거 raw데이터가 아니라 파라미터임)
    4. Vps_printf(" SGX3DSRV_LINK_IPQID_MULTIVIEW Height: %d Width:%d\n",
                pObj->inTskInfo[0].queInfo[pPrm->inQueParams[0].prevLinkQueId].chInfo[0].width,
                pObj->inTskInfo[0].queInfo[pPrm->inQueParams[0].prevLinkQueId].chInfo[0].height);
    저장된 파라미터 debug용 인건지.. 한번 print out해주고
    5. OSA_assert함수를 통해 각종 데이터들을 받을 공간을 만들어준다.
    6. input Resoultion(inputRes)을 확인해서 Widht를 기준으로 2MP, MP 기준 FRAME WIDTH한계를 맞춰주고
    7. eglWindowObj라는 구조체 내부 변수를 통해 memory를 세팅해둔다.
    8. eglWindowObj의 가로세로 맞춰주고 나면 본격적으로 데이터를 넣어준다.
    9. pObj->tskInfo.queInfo[0].chInfo[0] 이제 여기에 모든 채널의 정보를 우리가 가져온 파라미터대로 초기화시켜주고
    10. System_LinkChInfo *pPrevChInfo 라는 변수가
  pPrevChInfo = &(pObj->inQueInfo[inputQId].chInfo[channelId]); 로 큐의 채널 정보를 가져올 수 있도록 초기화 되어있다.
    11. OSA_queCreate() 로 localinputQ 의 핸들을 가져온다.
<br />
6) Sgx3DsrvLink_drvStart(pObj) 돌리고 Sgx3DsrvLink_tskRun(pObj, pTsk, &pMsg, &done, &ackMsg);
Sgx3DsrvLink_tskRun()) 함수만 보자면 (다시 sgx3DsrvLink_tsk.c에 있음.)

    1. OSA에서 터미널 명령 받아오고, SYSTEM_CMD_NEW_DATA인 경우 Sgx3DsrvLink_drvDoProcessFrames(pObj); 가 실행되는데 다시 sgx3DsrvLink_drv.c로 넘어가서 확인해보자.
    2. Sgx3DsrvLink_getInputFrameData(pObj)를 호출하는데, 이 함수는
    3. 내부에 System_getLinksFullBuffers 함수가 있음. pPrm->inQueParams[inputQId].prevLinkId, 와 같은 데이터를 매개변수로 받는데, pPrm = &pObj->createArgs; 로 위에 선언된 것을 보면 5-5 정도에서 input buffer size 와 타입을 정해준 부분과 같은 느낌.
    4. 이후 while문으로 진입하여 queue를 세고, queue에서부터 데이터를 얻는다. 
    OSA_queGet( &(pObj->localInputQ[SGX3DSRV_LINK_IPQID_PALUT].queHandle), (Int32 *) &pSystemBufferPALUT, OSA_TIMEOUT_NONE);
    5. pSystemBufferMultiview->chNum 에서 채널 id 따오고, 해당 채널로 데이터를 전송한다.
    6. pSystemBufferMultiview->bufType==SYSTEM_BUFFER_TYPE_VIDEO_FRAME_CONTAINER 직후에 YUV plane이야기가 나온다. 데이터 중 Y 채널에 대해서 정상적인 cropping이 작용할 것이고 UV채널들은 Y채널 직후에 데이터가 붙어서 나온다는 가정을 하고 있음.
    7. 데이터가 시작되는 좌표가 정상적으로 들어왔다면, startX!=0 || startY!=0
    offsetY 와 offsetUV를 정해주고, (pitch 1개 채널을 Y, 다음 채널을 UV로 사용하는 것으로 보인다.)
    8. pVideoCompositeFrame = (System_VideoFrameCompositeBuffer *)
                                        (pSystemBufferMultiview->payload);
    라고, System_VideoFrame전용 버퍼를 할당해 준다. 이 버퍼의 주소지를 videoCompositeFrame으로 정의하고
    9. videoCompositeFrame.bufAddr[0][0] ~ [1][3]까지 총 8개의 버퍼를 채워넣어 준다. 앞선 4개는 ([0][0]~[0][3]) Y채널 뒤는 UV 채널로 할당해주고
    10. 실 데이터를 넣어준다.
    texYuv[n] = System_eglGetTexYuv(&pObj->eglWindowObj, &texProp, videoCompositeFrame.bufAddr[0][n]); 또는
    texYuv[n] = System_eglWindowGetTexYuv(&pObj->eglWindowObj, &texProp, videoCompositeFrame.dmaFd[0][n]); 방식으로.
    11. 이때 System_eglWindowGetTexYuv 함수에 대해 알아보자면
    links_fw/src/hlos/system/system_gl_egl_util.c 에 있는 함수로,
    그 안에서 System_eglSetupYuvTexSurface 함수를 쓰는데 이때 dmaBufFd가 버퍼로 들어간다. 다시 해당 함수를 같은 파일내에서 찾아보면
    12. render_renderFrame(
                            &pObj->render3DSRVObj,
                            &pObj->eglWindowObj,
                            texYuv
                            );
    13. System_putLinksEmptyBuffers 는 links_fw/src/hlos/system/system_linkApi.c 에 있고
    버퍼를 free시켜주는 역할을 한다.
    14. GLuint는 unsigned int임