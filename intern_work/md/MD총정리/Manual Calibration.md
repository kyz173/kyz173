####Manual Calibaration

1. Calibaration의 기준이 되는 SIGN을 준비한다. 아래와 같은 이미지를 사용하는 것이 좋다.
<img src="/pictures/sign.png" alt="drawing" width="150"/>
</br>

2. SDK에서 ISS menu 로 진입한뒤, 3(calibaration menu) &rarr; 2(Manual) &rarr; 1(Save ISP output frames)를 입력하면, 화면에 나타나는 4개의 카메라 이미지가 YUV파일로 저장된다.
각 카메라마다 화면에 보이는 빨간색 네모에 sign이 하나씩 들어가도록 위치시킨다.
<img src="/pictures/calmenu.jpg" alt="drawing" width=""/>
<span style="color:green">(화면에 보이는 빨간 네모영역에 1.의 Sign을 인쇄하여 위치하도록 한다)</span>
저장되는 위치는 이전에 만들어두었던 BOOT 파티션 또는 그 내부에 만들어둔 TDA2X폴더이다.
</br>

3. 특이하게도, 다음단계를 진행하려면 Windows 환경이 필요하다. (Matlab을 활용하기 때문)
따라서 아래 경로의 폴더를 복사하여 Windows 환경으로 가져온다.
    `<설치파일>/vision_sdk/apps/tools/surround_vision_tools/3d_calibration_tool`
</br>

4. 8.4version의 MCR이 필요하니, 다운받고 이 이후를 진행하면 된다.
`<설치파일>/vision_sdk/apps/tools/surround_vision_tools/3d_calibration_tool/exe_out/main.exe`를 실행시켜 YUV 파일 4개를 불러오고, 프로그램에서 지시하는 대로 STEP1부터 STEP4까지 진행하면 된다. 이 부분은 UserGuide에 이상이 없으므로 
`<설치파일>/vision_sdk/docs/SurroundView/VisionSDK_UserGuide_3D_SurroundView_Manual_CalibTool.pdf` 를 참조
</br>

5. LUT 을 만들때는 카메라와 센서의 데이터 시트를 확인하여 설정해줘야 한다. 우리회사가 가지고 있는 OV2775 의 경우에는 Focal Length = 632 pixels 이다.
:bulb:일반적으로 사용하는 초점거리와 TI사에서 사용하는 프로그램의 초점거리 개념은 조금 차이가 있다. TI사에서 사용하고 있는 초점거리를 <span style="color:green">Focal Length</span>라고 표현하면
> <span style="color:green">Focal Length</span> = (실제Focal Length)/(sensor크기)*(해상도) pixels

이다.
예를 들어 1920x1080 FHD 해상도 이미지를 얻을 수 있는 카메라의 sensor부분 크기가 19.2mm x 10.8mm 이고, 실제Focal Length가 2mm 라면, <span style="color:green">Focal Length</span> = 2mm/10.8mm*1080 = 200 pixels 이다.

</br>

6. 결과
<img src="/pictures/cal_result.png" alt="drawing" width="200"/>