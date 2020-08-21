### c++ 문법구조 익히기

1. 함수 끝의 const는 무슨 의미인가?
```
class Foo 
{
public:
    int Bar(int random_arg) const
    {
        // code
    }
};
```
이 클래스 함수의 member variable을 바꾸지 못하게 하는 용도.
읽어들이는건 가능하지만, 교체하거나 write하지 못함.

2. cout << 
print를 위한 함수. 터미널 창에 << 로 연결된 모든 데이터를 python의 print("문자열",숫자,문자...) 등을 바로 프린트 해주듯 똑같은 기능을 한다.
```
std::cout << "안녕" << variable1 << " 문장끝" << endl;
 => '안녕(variable1의 값) 문장끝\n' 가 print된다.
```

3. class와 생성자 매소드

class 를 보면 이러한 특징이 도드라진다.
```
class Test
{
private:
	unsigned int important_variable ;
	// 주로 중요한 인수 등을 여기에 저장한다. private이기 때문에 다른 곳에서 접근해서 건드릴 수 없음.

public: // 아무곳에서나 접근 가능한 free한 아이들
	unsigned char not_important_variable;
	
	Test();
	// 기본 생성자. class를 사용하기 위해 사용한다.
	// 다른 곳에서 호출시 Test imsi; 등으로 imsi를 Test class 객채로 만드는 역할을 수행한다.
	// 그렇게 만들어진 imsi는 imsi.매소드() imsi.변수 등으로 class 객채로 사용가능	
	// 초기값으로 다른걸 주려면 Test(const std::string& filepath) 나 Test(int a, int b) 이런식의 변형도 가능함 다만,
	// 그랬을시에는 생성할 때 Test imsi(1,2) 이런식으로 함수에 매개변수를 전달해 주듯이 해야함.
	
	~Test(); 
	// 생성자 제거. 즉, 소멸자

	void Test_Function();
	// class의 매소드. 매개변수도 당연히 넣을 수 있다.
}
```
4. static_assert(상수표현식, 문자열)
> static_assert(size > 3, "size problem assert!!");

간단한 if -> error문구 출력용 지시문이라고 생각하면 된다.
상수표현식이 false인 경우에 문자열을 출력하면서 컴파일 프로세스가 중지됨.

5. template<>
 데이터 유형을 매개 변수로 전달하여 다른 데이터 유형에 대해 동일한 코드를 작성할 필요가 없도록하는 것
=> 데이터 유형에 따라 혹은 함수의 return타입에 따라 같은 함수를 여러개 작성해야하는 일이 발생할 수도 있는데, 그러한 귀찮음을 해결해주는 방법이라는 것.
```
template <typename T> 
T myMax(T x, T y) 
{ 
   return (x > y)? x: y; 
} 

... main에서
  cout << myMax<int>(3, 7) << endl;  // Call myMax for int 
  cout << myMax<double>(3.0, 7.0) << endl; // call myMax for double 
  cout << myMax<char>('g', 'e') << endl;   // call myMax for char 
```

처럼 간편하게 같은 형태의 여러 함수를 선언한 효과를 누릴 수 있음.

6. push_back
std::vector의 맴버변수인 push_back.
```
※함수원형
void push_back( const T& value );
void push_back( T&& value );        //C++11
```

https://shaeod.tistory.com/574


opengl glReadFixels
https://m.blog.naver.com/pkk1113/221128661359
https://www.khronos.org/registry/OpenGL/api/GLES3/gl31.h
https://stackoverflow.com/questions/3191978/how-to-use-glut-opengl-to-render-to-a-file