### TI사 TDA2PX evm board Seeting
TI chip sdk 설치 및 개발 환경 구성

#### 참고사항
:wrench: 개발환경 : LINUX (Ubuntu 18.04 LTS)

:package: 필요한 파일
http://software-dl.ti.com/processor-sdk-vision/esd/TDAx/vision-sdk/latest/index_FDS.html
 - PROCESSOR_SDK_VISION_03_08_00_00_setuplinux.bin (1.2GB)
 - tisdk-rootfs-image-dra7xx-evm_vsdk_3_8.tar.xz (100.9MB)

:pencil: 참고한 자료
+ [PROCESSOR_SDK_VISION_03_08_00_00_setuplinux.bin 을 설치하면 있는 docs 내부의 파일]
    + **Linux/VisionSDK_Linux_UserGuide** (most important)
    + VisionSDK_DataSheet.pdf
    + UserGuides/VisionSDK_UserGuide_TDA2px.pdf

+ [TI사에서 다운로드 받을 수 있는 파일]
    + **https://www.ti.com/tool/TDA2PXEVM - TDA2Px-ACD CPU EVM Board User`s Guide (Rev.A)**

<span style="color:red">:rotating_light:UserGuide오류!!</span>
TI사에서 제공하는 UserGuide에 오류가 상당히 많다. 해당 문구를 보게 되면 주의깊게 봐주세요.

:bulb: Userguide와 이 guide의 경로 혼동을 막기 위한 각주 (tda2px evm 환경)
```
$(MAKEAPPNAME) = apps
$(MAKECONFIG) = tda2px_evm_linux_all
```

---

#### 1. PROCESSOR_SDK_VISION 설치
`$> ./PROCESSOR_SDK_VISION_XX_XX_XX_XX_setuplinux.bin`
 (권한 오류 생기면 chmod +x 해주세요)
실행하고 설치프로그램대로 설치해주시면 됩니다.

**이 때 설치한 경로를 이하 <span style="color:green"><설치경로></span> 라고 표현**

---

#### 2. A15를 위한 컴파일러
* GCC Arm tool downloaded
    ** https://developer.arm.com/-/media/Files/downloads/gnu-a/8.3-2019.03/binrel/gccarm-8.3-2019.03-x86_64-arm-linux-gnueabihf.tar.xz **
    에서 다운로드 해서, `<설치경로>/ti_components/os_tools/linux/arm/` 에 넣어두고 압축을 해제한다.
    
    `$> tar –xvf gcc-arm-8.3-2019.03-x86_64-arm-linux-gnueabihf.tar.xz`
</br>

* Dependency <span style="color:red">:rotating_light:UserGuide오류!!</span>
    Guide에서 제시하는 대부분의 개발환경이 Ubuntu 14나 그 이전 버전이기 때문에 18.04LTS 개발환경에서는 몇 가지 추가사항이 필요하다.
    정상적인 개발환경 구성을 위해서는 32bit compile이 요구되어서 64bit환경인 18.04LTS에서는 다음과 같은 라이브러리 설치가 필요.
    `ia32-libs lib32stdc++6 lib32z1-dev lib32z1 lib32ncurses5 lib32bz2-1.0 libssl-dev`

    <span style="color:red">하지만</span> ia32-libs은 → lib32ncurses5, lib32z1로 대체
     lib32bz2-1.0는 더 이상 지원하지 않음. 따라서 다음을 따라 설치하면 된다.
    ```
    sudo apt-get install lib32stdc++6 lib32z1-dev lib32z1 lib32ncurses5 
    libssl-dev libgtk2.0-0:i386 libidn11:i386 libglu1-mesa:i386 libxmu6:i386
    ```

---

#### 3. One time PC setup
* vi나 vim과 같은 text editer로 .gitconfig 수정
    `$> vi /home/<username>/.gitconfig`
    ```
    [core]
    gitproxy = none for ti.com
    gitproxy = /home/<username>/git-proxy.sh
    ```
    save & exit
</br>

* git-proxy.sh 생성
    `$>vi /home/<username>/git-proxy.sh`
    ```
    exec /usr/bin/corkscrew proxyle01.ext.ti.com 80 $*
    ```
    save & exit
</br>

위 두 과정이 잘 되었다면
`$> git config --list` 를 입력했을때
```
core.gitproxy=none for ti.com
core.gitproxy=/home/<username>/git–proxy.sh
```
과 같은 결과가 나온다.

 :bulb: Code Compiler Studio는 취향껏 사용

---

#### 4. Install Linux Components
Essential Components kernel, uboot, sgx, and file system

TI사가 github에 올려둔 컴포넌트들을 다운로드 받는 과정이다. 단순히 다운로드 받을 뿐이기 때문에 창을 여러개 틀어서 동시에 진행해도 상관없다.

전용 sh파일이 있는데, `<설치경로>/vision_sdk/build/hlos/scripts/linux/setup_linux.sh` 잘 안되는 경우가 있어서 수동으로 직접 진행을 추천한다.

* omap (kernel)
    ```
    $> cd $INSTALL_DIR/ti_components/os_tools/linux/kernel
    $> git clone git://git.ti.com/glsdk/psdkla-kernel.git omap
    $> cd omap/
    $> git checkout -b kernel_dev tags/REL_VISION_SDK_03_08_00_00
    Or
    $> git checkout -b kernel_dev 3d03684
    ```
* cmem (kernel)
    ```
    $> cd $INSTALL_DIR/ti_components/os_tools/linux/kernel/cmem
    $> git clone git://git.ti.com/ipc/ludev.git
    $> cd ludev/
    $> git checkout -b cmem_dev 4f970f0
    Or 
    $> git checkout tags/4.16.00.00
    ```

* u-boot (u-boot)
    ```
    $> cd $INSTALL_DIR/ti_components/os_tools/linux/u-boot
    $> git clone git://git.ti.com/glsdk/psdkla-u-boot.git u-boot
    $> cd u-boot/
    $> git checkout -b uboot_dev tags/REL_VISION_SDK_03_08_00_00
    Or
    $> git checkout -b uboot_dev f454ae0
    ```

* sgx driver
    ```
    $> cd $INSTALL_DIR/ti_components/os_tools/linux/sgx
    $> git clone git://git.ti.com/graphics/omap5-sgx-ddk-linux.git
    $> cd omap5-sgx-ddk-linux/
    $> git checkout -b sgx_dev 4519ed3
    ```

* file system
    시작할때 받았던 tisdk-rootfs-image-dra7xx-evm_vsdk_3_8.tar.xz (100.9MB) 을 
    `<설치경로>/ti_components/os_tools/linux/targetfs` 에 압축해제시킨다.
    이때, build 하면서 이 위치를 read-write update하기 위해 targetfs 폴더만 chmod 777을 해주도록 한다. (내부에 압축해제할 파일들은 권한수정 x)

:bulb: optional components
    VisionSDK_Linux_Userguide의 2.4.2.2, (page 7) 파트.
    해당 파트는 여기서 다루지 않겠다. 필수적인 요소가 아니기 때문에 없어도 실행된다.

---

#### 5. Build

* makefile 수정
    `<설치경로>/vision_sdk/build` 에서 Rules.make를 찾아 다음과 같이 수정한다.
    TDA2PX기준 : MAKECONFIG=tda2px_evm_linux_all
</br>

* 빌드 (오랜시간이 소요됨)

    * u-boot kernel sgx driver
    ```
    $> cd <설치경로>/vision_sdk/build
    $> make linux
    $> make linux_install
    ```

    * SDK
    ```
    $>make –s –j depend
    $>make –s –j
    ```
    :bulb: -j4 처럼 여러 코어를 사용하면 속도가 향상될 수는 있지만, 정상적으로 빌드되지 않는경우가 있어서 싱글코어를 사용하는 것을 추천한다.
</br>

* uenv.txt수정 <span style="color:red">:rotating_light:UserGuide오류!!</span>
    빌드가 완료되면 `<설치경로>/vision_sdk/binaries/apps/tda2px_evm_linux_all/hlos/linux/boot`에 3개의 파일이 있게 되는데, 이 중 uenv.txt를 열어 다음과 같이 수정한다.
    `fdtfile=dra7-evm-infoadas.dtb` &rarr; `fdtfile=dra76-evm-infoadas.dtb`
</br>

* 다시 build하는 경우
    코딩 후 다시 build하는 일이 많은데, u-boot나 kernel, sgx driver에 변화가 없다면 SDK 수준에서의 build만 다시 하면 된다. (make -s -j depend부터) 그러나, 변화가 있다면 `<설치경로>/vision_sdk/binaries/` 폴더를 완전히 지우고 빌드의 처음부터 다시 진행해야한다. (make linux부터)
---

#### 6. SD card port <span style="color:red">:rotating_light:UserGuide오류!!</span>
* SD card porting
    `<설치경로>/vision_sdk/build/hlos/scripts/linux/mksdboot.sh` 파일이 sd카드에 필요한 boot file system 을 porting시켜주는 역할을 하는데, 몇 가지 문제가 있다.

    * 파티션 할당문제 :rotating_light:
     fdisk에서 두 개의 파티션을 할당해 각각의 device space name을 (이하 `${device}`) `${device}1`, `${device}2`로 설정되도록 하지만, 각 파티션을 포멧하고 파일시스템을 vfat(fat32)와 ext4로 설정할 때 `${device}p1`과 `${device}p2`를 부르도록 되어있다.
     &rarr; 따라서 mksdboot.sh 파일을 열어 161line과 167line의 `PARTITION1=${device}p1` 등의 p를 지워주면 정상작동한다.

    * rootfs 파일 복사문제 :rotating_light:
     빌드가 완료되었을때, rootfs 에 해당하는 부분을 다음경로에 자동으로 생성하게 된다.
     `<설치폴더>/ti_components/os_tools/linux/targetfs` 
     하지만 SD card에 port하는 mksdboot.sh 코드에는 이 경로에 있는 데이터를 못 가져가는 문제가 있다. 폴더 내의 모든 파일들을 `tisdk-rootfs-image-dra7xx-evm_vsdk_3_8.tar.xz` 로 압축하고, 직접 `<설치경로>/vision_sdk/binaries/apps/tda2px_evm_linux_all/hlos/linux/boot` 경로에 복사해주어 boot폴더 내부에 rootfs을 준비시켜줘야 한다.

    * dtb 파일 missing 문제 :rotating_light:
     build 과정중에 dtb 파일 (kernel)이 지정 폴더에 저장되지 못하는 경우가 있다.
     이런경우에 mksdboot.sh 과정에서는 오류메세지를 주지 않고, sd card 에 u-boot image, rootfs 은 정상적으로 복사가 된다. 하지만 실제로 보드에서 실행해보면 kernel 단에서 실행이 멈추고 dtb file을 찾을 수 없다는 메세지와 함께 할당할 수 없는 주소지라는 오류메세지를 내보냄.
     &rarr; 따라서 `<설치폴더>/ti_components/os_tools/linux/targetfs/boot/dra76-evm-infoadas.dtb` 해당 파일을 수동으로 SD card의 rootfs내부 boot폴더(dtb파일이 모인 폴더)에 복사해 줘야한다. (dtb가 저장되는 위치는 실행환경에 따라 조금 다를 수도 있으니 make중에 나온 log확인)
</br>

* 부족한 파일들 복사 ( 이미 되어있는 경우도 있음 )
    * Lens Module 복사
        <설치경로>/vision_sdk/apps/tools/surround_vision_tools/Srv_LUTs/TDA2X/CALMAT.bin
        <설치경로>/vision_sdk/apps/tools/surround_vision_tools/Srv_LUTs/TDA2X/CHARTPOS_RUBICON.BIN 
        을 SD Card /opt/vision_sdk로 복사한다.

    * Manual CALMAT setting
        직접 제작한 CALMAT이 존재하다면 SD card 의 boot에 TDA2X 라는 폴더를 만들어 그 안에 저장해둔다.
    
---

#### 7. boot mode switch 문제 <span style="color:red">:rotating_light:UserGuide오류!!</span>

SD card에서 부팅을 하도록 설정하려면 다음과 같은 보드 스위치 변경이 필요하다. 그런데 UserGuide에 설명되어있는 두 스위치 방식이 서로 다를 뿐만 아니라, Datasheet를 보면 오히려 표에 표기해둔 세번째 방법이 맞다.

SW3 | SW4 | 비고
------------ | ------------- | -------------
00001100 | 10000001 | (in tda2px user guide)
11100000 | 10000001 | (in linux user guide)
10101000 | 10000001 | works! << 이 방식을 추천한다.

---

#### 8. Uart 통신
keyboard interrupt를 활성화 시키기 위해서는 hard flow control 과 soft flow control을 모두 disable시켜줘야한다.

사용한 프로그램은 minicom (in linux) , Teraterm (in windows)

---

#### 9. Run & Camera Setting
* Start SDK
    1. 보드에 제작한 SD card를 넣고, mini 5pin 단자로부터 Usart통신을 준비. 전원을 인가하면 booting이 시작된다. 초기 root 비밀번호는 `root`
    2. 로그인이 완료되면 `$> cd /opt/vision_sdk`
    3. `source ./vision_sdk_load.sh` 로 build한 sdk사용준비
    4. `./apps` 실행
</br>

* Set resoultion and camera
    현재 우리회사에서 사용하고 있는 카메라 모듈은 OV2775 센서와 결합되어 사용되고 있다. 따라서 어플리케이션을 활용할때는 ISS menu를 선택하도록 하고, 환경은 다음과 같이 설정해둔다.
    `apps` 프로그램이 실행되면 Usart 터미널에 다음과 같이 입력한다.
    1. s -> 1 -> 2 (System setting for Display HDMI 1080 resoultion)
    2. s -> 2 -> 7 (System setting for link OV2775 module)
    3. 5 (ISS menu)
</br>

* About ISS menu applications
    1. single camera이미지를 받아 화면에 띄운다. default는 전면카메라
    2. 4개의 카메라로부터 calibration된 surround view 이미지를 화면에 띄운다. 이 작업은 사전에 생성시켜둔 CALMAT 등이 필요하다.
    3. CALMAT을 자동으로 만들거나, 수동으로 만들어진 CALMAT을 불러오는 메뉴이다.
        자동으로 CALMAT을 제작하려면(AUTO calibration된 메뉴) 조명이 밝고, SIGN이 또렷하게 상이 맺힌 상태에서 진행하는 것이 좋다.
        수동으로 제작된 CALMAT을 불러오려면 TDA2X 라는 폴더에서부터 필요한 CALMAT을 read 하고 적용시켜야 한다. (6번참고) 터미널 입력 순서는 2 -> 2 -> 3
    4. 실행조건은 2번과 다르지 않으며, BOWL 이미지를 화면에 띄운다.

