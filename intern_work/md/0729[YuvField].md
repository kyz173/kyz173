## 0729 YuvField

sgx3DsrvLink_drv.c 에서 
//TestDebug28
                Vps_printf("@@@@@@@@@@@@TestDebug28 start!!!@@@@@@@@@@@@");
                FILE* fp_input8;
                fp_input8 = fopen("TestDebug28.yuv","w");
                fwrite(pVideoCompositeFrame->bufAddr[0][0], 1280*720, 1, fp_input8); 
                fclose(fp_input8);
                Vps_printf("@@@@@@@@@@@@TestDebug28 end!!!@@@@@@@@@@@@");

을 Sgx3DsrvLink_drvDoProcessFrames(Sgx3DsrvLink_Obj *pObj) 안에 넣어서 일단 한 카메라의 Y 이미지 필드만 얻어낸 것 같음.

확인해보니 실제 resolution은 1280x720이 아니라 1920x1080이라서 수정이 필요함.



--- 확인결과
//TestDebug20 Front Ychennal
        Vps_printf("@@@@@@@@@@@@TestDebug20 start!!!@@@@@@@@@@@@");
        FILE* fp_input;
        fp_input = fopen("TestDebug20.yuv","w");
        fwrite(pVideoCompositeFrame->bufAddr[0][0], 1920*1080, 1, fp_input); 
        fclose(fp_input);
        Vps_printf("############TestDebug20 end!!!############");

//TestDebug21 Front UVchennal
        Vps_printf("@@@@@@@@@@@@TestDebug21 start!!!@@@@@@@@@@@@");
        FILE* fp_input1;
        fp_input1 = fopen("TestDebug21.yuv","w");
        fwrite(pVideoCompositeFrame->bufAddr[1][0], 1920*1080, 1, fp_input1);
        fclose(fp_input1);
        Vps_printf("############TestDebug21 end!!!############");

        //TestDebug22 Right Ychennal
        Vps_printf("@@@@@@@@@@@@TestDebug22 start!!!@@@@@@@@@@@@");
        FILE* fp_input2;
        fp_input2 = fopen("TestDebug22.yuv","w");
        fwrite(pVideoCompositeFrame->bufAddr[0][1], 1920*1080, 1, fp_input2); 
        fclose(fp_input2);
        Vps_printf("############TestDebug22 end!!!############");

//TestDebug23 Right UVchennal
        Vps_printf("@@@@@@@@@@@@TestDebug23 start!!!@@@@@@@@@@@@");
        FILE* fp_input3;
        fp_input3 = fopen("TestDebug23.yuv","w");
        fwrite(pVideoCompositeFrame->bufAddr[1][1], 1920*1080, 1, fp_input3);
        fclose(fp_input3);
        Vps_printf("############TestDebug23 end!!!############");




처럼 사용 할 수 있으며

offset주는 단 이후에 쓰면

//TestDebug30 Front Ychennal & offset?
        Vps_printf("@@@@@@@@@@@@TestDebug30 start!!!@@@@@@@@@@@@");
        FILE* fp_input30;
        fp_input30 = fopen("TestDebug30.yuv","w");
        fwrite(videoCompositeFrame.bufAddr[0][0], 1920*1080, 1, fp_input30); 
        fclose(fp_input30);
        Vps_printf("############TestDebug30 end!!!############");

//TestDebug31 Front UVchennal & offset?
        Vps_printf("@@@@@@@@@@@@TestDebug31 start!!!@@@@@@@@@@@@");
        FILE* fp_input31;
        fp_input31 = fopen("TestDebug31.yuv","w");
        fwrite(videoCompositeFrame.bufAddr[1][0], 1920*1080, 1, fp_input31);
        fclose(fp_input31);
        Vps_printf("############TestDebug31 end!!!############");

이런 방식도 같은 결과를 볼 수 있다.



생성된 texYuv가  render_renderFrame(
                            &pObj->render3DSRVObj,
                            &pObj->eglWindowObj,
                            texYuv
                            ); 로 가는 모습이 확인되었다. 이 함수의 pObj의 두 변수는
                                System_EglWindowObj eglWindowObj;
...

    /**< EGL object information */
    render_state_t render3DSRVObj;
    /**< 3D SRV rendering prgram obj */

    System_PvrScope_Obj pvrscopeObj;
    /**< object to hold the PVR SCOPE FIFO delails and profile Info */

    Sgx3DsrvLink_UpdateRenderCfgPrms renderCfgPrms;
    /**< User input params to update render configuration */

} Sgx3DsrvLink_Obj;
에서 정의되어있으며, render_state_t라는 타입은

typedef struct
{
   gl_state car_gl1;

   void * LUT3D;
   void * blendLUT3D;
   void * PALUT3D;
   void * BoxLUT;
   void * BoxPose3D;

#ifndef STANDALONE
   System_EglTexProperty texProp;
#endif
   int screen_width;
   int screen_height;

   uint32_t cam_width;
   uint32_t cam_height;
   uint32_t cam_bpp;

   EGLBoolean enableContinousTransitions;

} render_state_t;
의 형태로 구성되어있다.

render_renderFrame함수의 내부에
if(srv_param_bowl)
        srv_draw(pObj, texYuv, i);
if(srv_param_car)
        car_draw(i);
가 있어 srv_draw를 확인

void srv_draw(render_state_t *pObj, GLuint *texYuv, int viewport_id)
{
        int i;
        if(prevLUT != pObj->LUT3D || index_buffer_changed == true)
        {
                prevLUT = pObj->LUT3D;
                surroundview_init_vertices_vbo_wrap(pObj);
        }

        //First setup the program once
        glUseProgram(uiProgramObject);
        //then change the meshes and draw
        for(i = 0;i < QUADRANTS;i ++)
        {
                onscreen_mesh_state_restore_program_textures_attribs(
                                pObj, texYuv, (0+i)%4, (3+i)%4, viewport_id);
                onscreen_mesh_state_restore_vbo(
                                pObj, vboId[i*3], vboId[i*3+1], vboId[i*3+2]);
                GL_CHECK(onscreen_mesh_state_restore_vbo);
                glDrawElements(render_mode, index_buffers[active_index_buffer].length, GL_UNSIGNED_INT,  0);
                GL_CHECK(glDrawElements);
        }
        glFlush();
}
와 같이 생겼는데, onscreen ~ 부분이 현시할 데이터와 관련이 있어 보였다. 

저 onscreen 2개의 함수는 해석을 못하겠다. 예약되어있는 부분같음.
