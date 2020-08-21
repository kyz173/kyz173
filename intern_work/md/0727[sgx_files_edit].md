## 0727 sgx파일 변경하기.

빠른 build를 위한 팁
1. make -s -j depend -> make -s -j 로 변경이 완료되는 아이들은 apps.out파일 하나만 들고 가도 정상적으로 작동된다.
2. 컴파일러를 직접사용하면 문법 오류같은건 모두 찾아낼 수 있으니, make -s -j 돌리기 전에 미리 컴파일러로 돌려보고 시작하자 ( make -s -j 3분 가량 걸림 )

저번 md파일에서 sgx파일을 변경하는 것이 키워드가 될 수 있음을 파악하였다.
하지만, build과정에서 make -s -j depend와 make -s -j 를 하여도 sgx를 변경하기 위해서는 
make clean 하고 binary 폴더까지 전부지워주고 make linux와 make linux_install을 해줘야 한다. (u-boot와 kernel과 같은 단에서 생성됨)

+ grep -r "새로추가한내용" ./ 로 검색해가면서 binary file 인 apps.out에서도 이게 검출되는지 확인해보면 굳이 보드에서 테스트 해보지 않아도 결과를 알 수 있다.

그래서 그동안 make -s -j depend와 make -s -j 커맨드 만으로는 apps.out파일에서 grep -r "내가만든 함수이름" ./ 을 검색해보아도 나오지 않았던 것.
(apps.a 라이브러리 파일에는 생성된다만 실제로 실행되는 파일인 apps.out에 없으니 아무의미가 없다.)

+ 하나 찾은게, 저번에는 Sgx3DsrvLink_getInputFrameData 함수만 주구장창 봤으나, (여기에 printf구문중 "SGX Blending 뭐시기" 가 있음.) 잘 생각해보니 이 함수를 품고 있는 더 큰 함수
Sgx3DsrvLink_drvDoProcessFrames 를 사용하는 곳도 찾아봐야 하는게 맞다. 따라서 볼 파일이 하나 더 늘었음.
 >sgx3DsrvLink_tsk.c
바로 이 파일.

---



한 번에 한 시간 이상 걸리니 신중하게 마지막까지 검토하고 실행할 것.

---

