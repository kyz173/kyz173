### DisplayCapture 성공

보드에서 rendering된 이미지를 display로 띄우는데 이 영상을 Capture해서 저장하는데 성공하였다!

방법은 다음과 같다.

경로 : <설치경로>/vision_sdk/apps/src/hlos/modules/sgxRenderUtils/render.cpp

아래 코드를 1000번째 줄 정도에 있는 render_renderFrame 함수의 glViewport로 4채널 카메라 영상이미지를 screen에 띄우는 부분 뒤에 넣으면 잘 작동한다.



```
void render_renderFrame(render_state_t *pObj, System_EglWindowObj *pEglObj, GLuint *texYuv)

.... 중간생략

        //my_new_edit
        size_t size_whole = 1920*1080*4;
        unsigned char *readData = new unsigned char[size_whole];

        glReadPixels(0,0,1920,1080,GL_RGBA,GL_UNSIGNED_BYTE,readData);

        FILE *fp;
        fp = fopen("newtest.bmp","wb");
        fprintf(fp,"P6\n%d %d\n 255\n", 1920, 1080);

        for(int i = 0; i<1080; i++)
        {
                for(int j = 0; j<1920; j++)
                {
                        fwrite(&readData[(i*1920+j)*4],sizeof(GLbyte)*4,1,fp);
                }
        }
        delete[] readData;

        char *ScreenImageBuffer = (char*)malloc(1920*1080*4);
        FILE* OutputFile = fopen("newtest2", "wb");

        glReadPixels(0,0,1920,1080, GL_RGBA,GL_UNSIGNED_BYTE,ScreenImageBuffer);
        fwrite(ScreenImageBuffer,1920*1080*4,1,OutputFile);
        fclose(OutputFile);
        free(ScreenImageBuffer);
```

두번째 방법 (bmp파일 형식이 아닌 raw파일형식)이 더 나은 결과를 보였다. 아무래도 bmp는 LUT이 필요한데, 우리가 넣어주는 데이터는 아무런 헤더가 없어서 그런듯 보인다.

