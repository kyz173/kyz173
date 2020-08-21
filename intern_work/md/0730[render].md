## 0730 Display단 조사


1. 
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
 이게 있길래 확인중.

2. 
DisplayMpLink_drvStart 이 함수는 파일 tsk.c 에 있길래 확인.
```
DisplayMpLink_tskMain(struct Utils_TskHndl_t *pTsk, Utils_MsgHndl *pMsg)
{
    UInt32 cmd = Utils_msgGetCmd(pMsg);
    Bool ackMsg, done;
    Int32 status = SYSTEM_LINK_STATUS_SOK;
    DisplayMpLink_Obj *pObj = (DisplayMpLink_Obj *) pTsk->appData;
...
if(status == SYSTEM_LINK_STATUS_SOK)
    {
        /*
         * Create command received, create the driver
         */
        status = DisplayMpLink_drvCreate(pObj, Utils_msgGetPrm(pMsg));

        /* ACK based on create status */
        Utils_tskAckOrFreeMsg(pMsg, status);
    }

}
```

3. DisplayMpLink_tskMain 에서 pMsg는 message handle이고, 이게 도착해야 실행한다.
 그럼 이 메세지는 어디서 오는거지? 모르겠다..!
 
--- 다른방식

4. drv 에서 texYuv로 옮길때 System_eglGetTexYuv 를 쓴다
link_sw에 있어서 뒤져보니
System_eglSetupYuvTexSurface 로 연결됨. (System_eglGetTexYuv와 같은 변수들을 들고 간다.)

static GLuint System_eglSetupYuvTexSurface(System_EglObj *pObj, System_EglTexProperty *pProp, void *bufAddr, int texIndex) 
이게 전부인것을 보니 그냥 구조체화? multi 변수화? 시켜주는 애로 판단. 진짜 데이터 처리는 그럼 이쪽이 아니다.

이후에 render_renderFrame에서 마치 하나의 변수처럼 쉽게 다루기 위해서 만든 녀석 같음

+ render에서 시점 변환하거나 옮기는 코드 여기있음.
> vim ./apps/src/hlos/modules/sgxRenderUtils/render.cpp

```
typedef struct _srv_viewport_t
{
        unsigned int x;
        unsigned int y;
        unsigned int width;
        unsigned int height;
        bool animate;
} srv_viewport_t;

srv_viewport_t srv_viewports[] = {
        {
                x : 0,
                y : 0,
                width : 960,
                height: 1080,
                animate: true,
        },
        {
                x : 960,
                y : 0,
                width : 960,
                height: 1080,
                animate: false,
        }
};
```

어쩔수 없이 onscreen_mesh_state_restore_program_textures_attribs 함수를 봤는데
texYuv 가 역시 각각의 카메라에서 들어오는 데이터를 담당하는 변수화 되었고( 상기 설명한 System_eglSetupYuvTexSurface 로 인해서 )
 0번과 1번, 1번과 2번 ... 3번과 0번 이런식으로 쌍을 지어서 데이터 처리를 하는 것으로 보인다.

---

./apps/src/rtos/alg_plugins/autocalibration/include/globalDefs.h
./apps/src/rtos/modules/display_multi_pipe/displayMultiPipe_tsk.c
./links_fw/src/rtos/links_ipu/vip_capture/captureLink_drv.cvim ./links_fw/src/hlos/system/system_gl_egl_utils.c
./apps/src/hlos/modules/sgxRenderUtils/srv.cpp 
./apps/src/hlos/modules/sgxRenderUtils/render.cpp

void render_renderFrame(render_state_t *pObj, System_EglWindowObj *pEglObj, GLuint *texYuv)
{
	if(srv_render_to_file == true)
		set_coords_transition(0, srv_param_view1, srv_param_view2, srv_param_step);

#ifndef _WIN32
	if(prev_time_usecs == 0)
	{
		gettimeofday(&tv, NULL);
		prev_time_usecs = 1000000 * tv.tv_sec + tv.tv_usec;
	}
#endif

	shader_output_select = srv_param_select;
	glClear(GL_COLOR_BUFFER_BIT);
	{
		for(int i = 0; i < num_viewports; i++)
		{
			if(srv_viewports[i].animate == true)
			{
				if( (animatengap[i] == false) && (pObj->enableContinousTransitions == false) )
				{
					/* stay here for gap number of frames;
					 *
					 */
					step[i]++;
					if(step[i] >= gap)
					{
						step[i] = 0;
						animatengap[i] = true;
					}
				}
				else
				{

                                    if (pObj->enableContinousTransitions == true)
                                    {
                                        if (current_index[i] == (num_srv_views-1))
                                        {
                                            increasingView = false;
                                        }

                                        if (current_index[i] == 2)
                                        {
                                            increasingView = true;
                                        }

                                        if (increasingView)
                                        {
					    next_index=(current_index[i] + 1)%(num_srv_views);
					    if (next_index == 0 || next_index == 1)
					    {
					        next_index = 2;
					    }
                                        }
                                        else
                                        {
					    next_index=(current_index[i] - 1)%(num_srv_views);
					    if (next_index == 0 || next_index == 1)
					    {
					        next_index = 2;
					    }
                                        }

                                        COORD_TRANSITION_SMOOTH(i, camx, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, camy, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, camz, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, targetx, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, targety, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, targetz, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, anglex, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, angley, next_index, step[i]);
                                        COORD_TRANSITION_SMOOTH(i, anglez, next_index, step[i]);
                                        render_updateView();
                                        step[i]++;
                                        if(step[i] >= num_iterations)
                                        {
						step[i] = 1;
						animatengap[i] = false;
						current_index[i] = next_index;
						set_coords(0, current_index[i]);
                                        }
                                    }
                                    else
                                    {
                                        next_index=(current_index[i] + 1)%(num_srv_views);
                                        COORD_TRANSITION(i, camx, next_index, step[i]);
                                        COORD_TRANSITION(i, camy, next_index, step[i]);
                                        COORD_TRANSITION(i, camz, next_index, step[i]);
                                        COORD_TRANSITION(i, targetx, next_index, step[i]);
                                        COORD_TRANSITION(i, targety, next_index, step[i]);
                                        COORD_TRANSITION(i, targetz, next_index, step[i]);
                                        COORD_TRANSITION(i, anglex, next_index, step[i]);
                                        COORD_TRANSITION(i, angley, next_index, step[i]);
                                        COORD_TRANSITION(i, anglez, next_index, step[i]);
                                        render_updateView();
                                        step[i]++;
                                        if(step[i] >= num_iterations)
                                        {
						step[i] = 0;
						animatengap[i] = false;
						current_index[i] = next_index;
                                        }
                                    }
				}
			}
			else
			{
                                if (pObj->enableContinousTransitions == true)
                                {
				    step[i] = num_iterations;
				    current_index[i] = 2;
                                }
			}

			glViewport(srv_viewports[i].x,
					srv_viewports[i].y,
					srv_viewports[i].width,
					srv_viewports[i].height);

			if(srv_param_bowl)
				srv_draw(pObj, texYuv, i);
			if(srv_param_car)
				car_draw(i);
		}
		//boxes_draw((ObjectBox *)pObj->BoxLUT, (Pose3D_f *)pObj->BoxPose3D, texYuv);
	}
	char* ch = (char*)"HIHI.tga";
	Screendump(ch, 1920, 1080);
	Vps_printf("################ HIHI.tga success #################");
#if ENABLE_SGX_RENDERED_PREVIEW
	// Draw the other panes
	{
		glViewport(0, 1080-(200+440*1),520,440);
		//screen1_draw_vbo(texYuv[0]);
	}
	{
		glViewport(0, 1080-(200+440*2),520,440);
		//screen1_draw_vbo(texYuv[1]);
	}
	{
		glViewport(520+880, 1080-(200+440*1),520,440);
		//screen1_draw_vbo(texYuv[2]);
	}
	{
		glViewport(520+880, 1080-(200+440*2),520,440);
		//screen1_draw_vbo(texYuv[3]);
	}
#endif

#ifndef _WIN32
	if(frame_count < 100)
	{
		frame_count++;
	}
	else
	{
		frame_count = 0;
		gettimeofday(&tv, NULL);
		cur_time_usecs = 1000000 * tv.tv_sec + tv.tv_usec;
		delta_usecs = cur_time_usecs - prev_time_usecs;
		fps = 100.0f/((float)delta_usecs/1000000.0f);
		prev_time_usecs = cur_time_usecs;
		RENDER_PRINT("%f fps\n", fps);
	}
#endif
}


결국 opengl을 공부해야 이해할 수 있을 것 같아서 opengl을 공부하기로 했다.

char* ch = (char*)"HIHI.tga";
	Screendump(ch, 1920, 1080);
	Vps_printf("################ HIHI.tga success #################");

부분은 새로 내가 추가한 함수.

void Screendump(char *tga_file, short W, short H) {
 FILE   *out = fopen(tga_file, "w");
 char   pixel_data[3*W*H];
 short  TGAhead[] = {0, 2, 0, 0, 0, 0, W, H, 24};

 glReadBuffer(GL_FRONT);
 glReadPixels(0, 0, W, H, GL_BGR, GL_UNSIGNED_BYTE, pixel_data);
 fwrite(&TGAhead, sizeof(TGAhead), 1, out);
 fwrite(pixel_data, 3*W*H, 1, out);
 fclose(out); }

기존 설정에는 glReadBuffer와 glReadPixels 함수가 없어서 render.h에 GLES3/gl31.h을 따로 추가해주었다. (ifndef 나 ifdef사이에 껴서 괜히 window환경일때만 build되도록 해놓고 오류내지 말자 바보야.)



1. void glDrawElements(	GLenum mode,
 	GLsizei count,
 	GLenum type,
 	const void * indices);
https://www.khronos.org/registry/OpenGL-Refpages/es2.0/xhtml/glDrawElements.xml

2. void glVertexAttribPointer(	GLuint index,
 	GLint size,
 	GLenum type,
 	GLboolean normalized,
 	GLsizei stride,
 	const void * pointer);
https://www.khronos.org/registry/OpenGL-Refpages/es2.0/xhtml/glVertexAttribPointer.xml

3. void glBindBuffer(	GLenum target,
 	GLuint buffer);
https://www.khronos.org/registry/OpenGL-Refpages/es2.0/xhtml/glBindBuffer.xml

4. void glUseProgram(	GLuint program);
https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glUseProgram.xml

5. void glUniformMatrix4fv(	GLint location,
 	GLsizei count,
 	GLboolean transpose,
 	const GLfloat *value);
https://www.khronos.org/registry/OpenGL-Refpages/es2.0/xhtml/glUniform.xml

6. void glReadPixels(	GLint x,
 	GLint y,
 	GLsizei width,
 	GLsizei height,
 	GLenum format,
 	GLenum type,
 	void * data);
https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glReadPixels.xml

7. void glReadBuffer(	GLenum mode);
https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glReadBuffer.xml

