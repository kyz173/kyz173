## 0728 display 버퍼 가로채기

오늘은 Calibration까지 완료된 ISS - 2 번 옵션 최종 영상이 뜰 때 
"SGX3DSRV Link - Blending LUT received !!!" 라는 메세지가 뜨는 것을 이용해서 그 바로 위에 있는

OSA_memCacheInv 함수에 대해 탐구해본다.
이 함수는 ./links_fw/src/hlos/osa/src/osa_mem.c 에 선언되어있다.

1) nullLink_tsk 용례
 null link를 만드는 ./links_fw/src/hlos/links_a15/null/nullLink_tsk.c
코드에서도 쓰이고 있다.
 -> 특히 여기서는 fpDataStream[chNum] 에 저장하도록 되어있음.
```
OSA_memCacheInv((UInt32)pVidBuf->bufAddr[1], (pChInfo->pitch[0]* pChInfo->height));
fwrite(pVidBuf->bufAddr[0], (pChInfo->pitch[0]* pChInfo->height), 1, pObj->fpDataStream[chNum]);
```
한 번 이 버퍼를 저장해서 빼봐야겠다.


---
2) nullSrc display 용례
./sample_app/src/hlos/usecases/nullSrc_display/chains_nullSrcDisplay.c 에서
```
chains_nullSrcDisplayObj gUcObj;

chains_nullSrcDisplay_Create(&gUcObj,NULL);
fillSrcBuf(&gUcObj);
chains_nullSrcDisplay_Start(&gUcObj);
```
구조로 뽑길래 확인이 필요하다.

여기서 System_VideoFrameBuffer *pVideoFrame 을 선언하여 쓰고,
pVideoFrame->bufAddr[0], pVideoFrame->bufAddr[1] 등으로 실 버퍼로 쓰는 것 같음.
 '1)'에서는 System_VideoFrameBuffer *pVidBuf 로 사용되었기 때문에 충분히 가능성이 있다.

---
3) _drv 파일에서

System_buffer * pSystemBufferMultiview 라는 변수를 사용.
pSystemBufferMultiview->bufType==SYSTEM_BUFFER_TYPE_VIDEO_FRAME_CONTAINER 라는 문구가 있는걸 봐서는, 이걸 video frame buffer로 쓰는 것으로 보인다.


---




### yuv파일에 대하여

+ yuv420
 24bit rgb place를 12bit로 표현한다. Y정보는 8bit(full data) U와 V가 2bit씩.
![Github logo](./0728pictures/yuv420.png) 

> http://egloos.zum.com/praise4/v/1742236 << 자세한 설명

4가지 종류가 있다. YV12 NV12 IMC2 IMC4
1. YV12
 메모리 순서대로 Y->V->U 잡혀있다. 간혹 Stride 정보라고 해서 각 라인당 여분 메모리가 붙어있는 경우도 있으니 주의.
![Github logo](./0728pictures/yuv420_1.gif)
2. NV12
 첫 블록은 Y만. 이후에는 U0->V0->U1->V1->... 반복
![Github logo](./0728pictures/yuv420_2.gif)
3. IMC2
 첫블록은 Y만, 이후로는 height bit수 기준으로 앞 절반은 V, 뒤 절반은 U가 이어진다.
![Github logo](./0728pictures/yuv420_3.gif)
4. IMC4
 3과 같으나 VU 순서가 아니라 UV순서.
![Github logo](./0728pictures/yuv420_4.gif)

+ yuv파일의 첫번째 프레임 값 offset
> Y = 0 ~ resolution - 1
 U = resolution ~ (resolution + resolution / 4) - 1
 V = (resolution + resolution / 4) ~ (resolution + resolution / 4 + resolution / 4) - 1 
결국 한 프레임의 크기는 resoultion + resolution / 2 이며, 다음 프레임의 위치는 (resolution + resolution / 2) ~ (3 * resolution) - 1 이다.

