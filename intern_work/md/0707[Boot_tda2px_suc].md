##0707 : 김용준 주간 업무 보고
### TDA2PX evm board setting
TI chip sdk 설치 및 개발 환경 구성
_Texas Instruments 사의 TDA2PX evm 보드를 받아 u-boot image와 kernel, rootfs을 build해 porting을 시도._

참고한 자료
**Linux/VisionSDK_Linux_UserGuide** (most important)
**https://www.ti.com/tool/TDA2PXEVM - TDA2Px-ACD CPU EVM Board User`s Guide (Rev.A)**
VisionSDK_DataSheet.pdf
UserGuides/VisionSDK_UserGuide_TDA2px.pdf


대부분은 참고자료대로 따라갔지만, Linux UserGuide에 몇 가지 문제가 있어 수정이 필요하다.


###1. Ubuntu version 문제

Guide에서 제시하는 대부분의 개발환경이 Ubuntu 14나 그 이전 버전이기 때문에 18.04LTS 개발환경에서는 몇 가지 추가사항이 필요하다.

정상적인 개발환경 구성을 위해서는 32bit compile이 요구되어서 64bit환경인 18.04LTS에서는 다음과 같은 라이브러리 설치가 필요.

_ia32-libs lib32stdc++6 lib32z1-dev lib32z1 lib32ncurses5 lib32bz2-1.0 libssl-dev_

하지만 ia32-libs은 → lib32ncurses5, lib32z1로 대체되었고, lib32bz2-1.0는 더 이상 지원하지 않음. 따라서 다음을 따라 설치하면 된다.
```
sudo apt-get install lib32stdc++6 lib32z1-dev lib32z1 lib32ncurses5 
libssl-dev libgtk2.0-0:i386 libidn11:i386 libglu1-mesa:i386 libxmu6:i386
```

###2. file 명 수정
3.1.2 SD only boot에 기술된 문장에 오타가 존재함.
fdtfile=dra7-evm-infoadas.dtb -> fdtfile= dra76-evm-infoada*s*.dtb


###3. SD card init 문제
4.2 에서 sd card를 준비할 때 사용하게 되는 mksdboot.sh shell script파일은 fdisk에서 두 개의 파티션을 할당해 각각의 device space name을 sdb1 sdb2로 설정되도록 하지만, 각 파티션을 포멧하고 파일시스템 을 vfat(fat32)와 ext4로 설정하는데는 sdbp1과 sdbp2를 부르도록 설정해두어서 문제가 생김.
mksdboot.sh 파일을 열어 161line과 167line의 PARTITION1=${device}p1 등의 p를 지워주면 정상작동한다.


###4. dtb 파일 missing 문제
mksdboot.sh를 사용하면 sd card 에 u-boot image, rootfs 은 정상적으로 복사가 되는데, 실행해보면 kernel 단에서 실행이 멈추고 dtb file을 찾을 수 없다는 메세지와 함께 할당할 수 없는 주소지라는 오류메세지를 내보내는 버그가 있었음.
```
<설치폴더>/ti_components/os_tools/linux/targetfs/boot/dra76-evm-infoadas.dtb
```
해당 파일을 수동으로 sd card의 boot partition에 복사해 줘야한다. (실행환경에 따라 조금 다를 수 도 있으니 make 중에 나온 log 확인)


###5. boot mode switch 문제
SW3 | SW4 | 비고
------------ | ------------- | -------------
00001100 | 10000001 | (in tda2px user guide)
11100000 | 10000001 | (in linux user guide)
10101000 | 10000001 | works! << 이 방식을 추천한다.


###6. minicom 으로 uart 통신.
keyboard interrupt를 활성화 시키기 위해서는 hard flow control 과 soft flow control을 모두 disable시켜줘야한다.
