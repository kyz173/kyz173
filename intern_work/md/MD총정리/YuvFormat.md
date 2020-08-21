###YUV Format

YUV포멧의 특징 중 하나는, 헤더파일이 따로 없다는 것

* yuv420
 24bit rgb place를 12bit로 표현하는 포멧이다. Y정보는 8bit(full data) U와 V가 2bit씩.
<img src="/pictures/yuv420.png" alt="drawing"/>
> http://egloos.zum.com/praise4/v/1742236 << 에서 자세한 설명을 볼 수 있다.

</br>

* 세부분류
    4가지 종류가 있다. YV12 NV12 IMC2 IMC4
    1. YV12
    메모리 순서대로 Y->V->U 잡혀있다. 간혹 Stride 정보라고 해서 각 라인당 여분 메모리가 붙어있는 경우도 있으니 주의.
    <img src="/pictures/yuv420_1.gif" alt="drawing"/>
    2. NV12
    첫 블록은 Y만. 이후에는 U0->V0->U1->V1->... 반복
    <img src="/pictures/yuv420_2.gif" alt="drawing"/>
    3. IMC2
    첫블록은 Y만, 이후로는 height bit수 기준으로 앞 절반은 V, 뒤 절반은 U가 이어진다.
    <img src="/pictures/yuv420_3.gif" alt="drawing"/>
    4. IMC4
    3과 같으나 VU 순서가 아니라 UV순서.
    <img src="/pictures/yuv420_4.gif" alt="drawing"/>
</br>

* yuv파일의 첫번째 프레임 값 offset
 Y = 0 ~ resolution - 1
 U = resolution ~ (resolution + resolution / 4) - 1
 V = (resolution + resolution / 4) ~ (resolution + resolution / 4 + resolution / 4) - 1 
   * 결국 한 프레임의 크기는 resoultion + resolution / 2 이며, 다음 프레임의 위치는 (resolution + resolution / 2) ~ (3 * resolution) - 1 이다.

