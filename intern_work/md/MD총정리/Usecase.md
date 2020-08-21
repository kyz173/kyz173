### Usecase

:rotating_light:중요한 점 : MAKECONFIG = tda2px_evm_linux_all 옵션을 사용하기 때문에 linux기반 A15 위에서 작동하게 된다.
=> rtos의 usecase는 그대로 사용할 수 없다. (사용하는 함수, 메커니즘이 다름) hlos를 봐야한다.

RTOS (Real Time Operating System)
HLOS (high level Operating System)

`<설치경로>/vision_sdk/apps/src/hlos/adas/src/usecases/`
안에 있는 usecase를 보고 수정

:bulb: Userguide와 이 guide의 경로 혼동을 막기 위한 각주 (tda2px evm 환경)
```
$(MAKEAPPNAME) = apps
$(MAKECONFIG) = tda2px_evm_linux_all
```

---

#### 1. new Usecase 제작
* 다른 usecase를 참고하여 txt 파일를 하나 만든다.
	예를들어 single camera를 위한 display일 때 이렇게 작성된다.
	```
	Usecase : chains_vipSingleCam_Display

	Capture -> Display_Video
	GrpxSrc -> Display_Grpx
	```
	각 요소들은 사전에 정해져있는 예약어 취급을 당하기 때문에, 다른 usecase에서 활용중인 이름들 외에 다른 이름으로는 정상작동하지 않을 수도 있다.
	(이들 예약어들을 정리한 시트는 찾지 못하였다.)
	:bulb: 따라서 이 작업은 TI에서 지원하는 하드웨어나 프로세서와 제작할 Usecase 코드와의 링크를 담당하는 부분이라고 생각해야한다.
	이 txt파일을 지금부터 <span style="color:blue">newUsecase.txt</span> 라고 하겠다.
</br>

* Usecase priv 파일 생성
	`<설치경로>/vision_sdk/apps/tools/vision_sdk_usecase_gen/bin/vsdk_linux.out`
	해당 프로그램을 이용하여 priv header와 priv source code를 생성시킬 수 있다.
	input으로 <span style="color:blue">newUsecase.txt</span>를 사용한다.
	`vsdk_linux.out -file <새로만든usecase.txt> <코드out시킬경로>`
	이렇게 하면 <span style="color:blue">newUsecasepriv.c</span>와 <span style="color:blue">newUsecasepriv.h</span>라는 파일들이 생성될텐데, 이들을 include해서 원하는 동작을 하는 c파일을 제작해주면 된다. 
	이 c파일을 지금부터 <span style="color:green">newUsecase.c</span> 라고 하겠다.
</br>

* 코드작성
	<span style="color:green">newUsecase.c</span> 를 작성한다.

---

#### 2. new Usecase 빌드옵션 추가
	
* 새로만든 usecase가 있는 폴더에 MAKEFILE.MK를 추가시킨다. 보통 빌드시에 다른 환경에서 MAKE해줄 이유가 없다면, 이 파일은 다른 usecase에 있는 MAKEFILE.MK을 들고오면 된다.
</br>

* cfg.mk 파일을 생성한다
	이 usecase를 사용할 때 계산을 활성화 시킬 CPU를 할당하거나, 알고리즘 플러그인의 사용여부를 확인하는 폴더이다. 
	CPU는 (TDA2PX EVM의 경우) IPU1_0, IPU1_1, IPU2, DSP1, DSP2, EVE1, EVE2, EVE3, EVE4, A15_0 중에서 선택할 수 있으며, 필요한 CPU의 활성화를 위해서는 다음과 같이 입력해두면 된다.
	`NEED_PROC_IPU1_0 = yes`
	ALG plugin 의 경우도 필요한 알고리즘 플러그인이 위치하는 폴더이름을 가져와서 CPU할당예시처럼 yes로 설정해두면 된다.
</br>

* main config 수정
	<span style="color:red">주의!</span>usecase폴더 내의 cfg.mk가 아니다.
	`<설치경로>/vision_sdk/apps/configs/cfg.mk`
	해당 cfg.mk파일을열어 우리가 새로 만든 usecase를 build하도록 추가해준다.
	```
	LINUX_TDA2XX_UC_LIST = \
	UC_avbrx_dec_display \
	...
	UC_new_usecase ★
	```
	★ 표시처럼 Usecase list에 추가해주면 된다.
</br>

* build config 수정
	`<설치경로>/vision_sdk/apps/configs/tda2px_evm_linux_all/uc_cfg.mk`
	main config에서 추가해두었던 list를 프로그램 빌드시에 여기서 flag를 만들어 보내주는 역할을 한다.
	새로만든 flag를 yes로 추가해둔다.
	`UC_new_usecase = yes`
</br>

* build 후 usecase의 적용여부 확인법
	make showconfig를 해주면, 내가 생성한 usecase가 있는지 확인이 가능하다.
	`#Use-cases include in build` 에서 확인
	같은방법으로 algorithm도 확인가능
	`#Alg plugins included in build`

---

#### 3. main에서 확인
* chains_main.c 과 같은 파일에서
 ```
 #ifdef UC_new_usecase
  //new_usecase_함수(&gChains_usecaseCfg);
 #endif 
 "\r\n "
 ```
  등으로 테스트가 가능하다.

---

#### 4. 빌드가 완료되고 실행하기 전 확인할 점
* rootfs가 최신버전이 아니에요
	usecase를 만들거나 수정하고 나서 다시 make -s -j depend 와 make -s -j로 빌드를 진행할때 rootfs의 apps.out이 수정되고 자동으로 `<설치경로>/ti_components/os_tools/linux/targetfs`에 저장된다. 이 폴더를 다시 압축하여(.tar.xz) vision_sdk/binaries/apps/tda2px_evm_linux_all/hlos/linux/boot 여기에 옮겨놓아야 mksdboot.sh를 사용한 sd card 포팅이 된다.
</br>

* LENS.BIN이나 CALMAT.BIN등의 파일들을 넣었는지 확인하자
  LENS.BIN이 없으면 카메라 이미지를 받아오지 못하며
  CALMAT이 없으면 ISS 싱글카메라만 실행되고 나머지는 Unsupported option이라는 디폴트 메세지가 출력된다.