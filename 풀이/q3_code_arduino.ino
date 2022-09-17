#pragma GCC optimize ("-O3")

// type definition
typedef unsigned char u8;
typedef unsigned short u16;

// rotation left function
#define ROL(X, Y) ((X<<Y) | (X>> (8-Y))) // optimization
#define ROL_4BIT(X, Y) ((X<<Y) | (X>> (4-Y))) // optimization

#define T1(B,C,D,E) (B & C) | (D & E)
#define T2(F,G,H) (F ^ G ^ H)
#define DATA_SIZE 4
#define SIZE_TEXT 32

u8 init_constant[8] = {0xAA, 0x11, 0xBB, 0x22, 0xCC, 0x33, 0xDD, 0x44};
u8 init_constant2[4] = {0x12, 0x34, 0x56, 0x78};

// https://eprint.iacr.org/2017/622.pdf (GIFT block cipher)
u32 s_box[16] = {0x1, 0xa, 0x4, 0xc, 0x6, 0xf, 0x3, 0x9, 0x2, 0xd, 0xb, 0x7, 0x5, 0x0, 0x8, 0xe};

void byte_permutation(u8* inout){
    u8 tmp;

    tmp = inout[7];
    inout[7] = inout[6];
    inout[6] = inout[5];
    inout[5] = inout[4];
    inout[4] = inout[3];
    inout[3] = inout[2];
    inout[2] = inout[1];
    inout[1] = inout[0];
    inout[0] = tmp;
}

void Func1(u8* in, u8* out){ 
    u32 i=0;
    u8 tmp1, tmp2;
    u8 func1_tmp[8] = {0,};

    //constant initialization
    for(i=0;i<8;i++){
        func1_tmp[i] = init_constant[i]; 
    }

    for (i = 0; i < 16; i++) {
        //computation
        tmp1 = T1(func1_tmp[1], func1_tmp[2], func1_tmp[3], func1_tmp[4]);
        tmp2 = T2(func1_tmp[5], func1_tmp[6], func1_tmp[7]);

        func1_tmp[0] = func1_tmp[0] + tmp1 + tmp2;
        func1_tmp[0] = func1_tmp[0] + in[i%4];
        func1_tmp[0] = ROL(func1_tmp[0],1);
        //permutation
        byte_permutation(func1_tmp);
    }

    for(i=0;i<4;i++){
        out[i] = func1_tmp[i] ^ func1_tmp[i+4];
    }
}

void byte_to_bit(u8* in, u8* out, u32 size_bit) {
    u32 size_byte = size_bit / 8;
    u32 i, j;
    u8 bit_selector = 1;

    for (i = 0; i < size_byte; i++) {
        bit_selector = 1;

        for (j = 0; j < 8; j++) {
            if (in[i] & bit_selector){
                out[i * 8 + j] = 1;
            }else{
                out[i * 8 + j] = 0;
            }
            bit_selector = bit_selector << 1;
        }
    }
}

void bit_to_byte(u8* in, u8* out, u32 size_bit) {
    u32 size_byte = size_bit / 8;
    u32 i, j;

    for (i = 0; i < size_byte; i++) {
        out[i] = 0;
        for (j = 0; j < 8; j++) {
            out[i] = out[i] + (in[i * 8 + j] << j);
        }
    } 
}

void PERMUTATE_FUNC(u8* in, u8* out) {
    u8 text_tmp[SIZE_TEXT];
    u32 i, j;

    for (i = 0; i < 4; i++) {
        for (j = 0; j < 8; j++) {
            text_tmp[i * 8 + j] = in[i + j * 4];
        }
    }

    for (i = 0; i < SIZE_TEXT; i++) {
        out[i] = text_tmp[i];
    }
}

void Func2(u8* in, u8* out){
    u8 func2_tmp[4] = {0,};
    u8 func2_key[4] = {0,};

    u8 func2_bit_tmp1[32] = {0,};
    u8 func2_bit_tmp2[32] = {0,};

    u8 tmp1, tmp2;
    u8 cnt;
    int i,j=0;

    func2_key[0] = in[0]^init_constant2[0];
    func2_key[1] = in[1]^init_constant2[1];
    func2_key[2] = in[0]^init_constant2[2];
    func2_key[3] = in[1]^init_constant2[3];
    func2_tmp[0] = in[2];
    func2_tmp[1] = in[3];
    func2_tmp[2] = in[2];
    func2_tmp[3] = in[3];

    for(i=0;i<16;i++){ 
        cnt = i;

        for(j=0;j<4;j++){
            func2_key[j] = func2_key[j]^cnt;
            tmp1 = s_box[ (func2_tmp[j]&0xF) ];
            tmp2 = (s_box[ (( func2_tmp[j]>>4 ) & 0xF) ]) & 0xF;

            func2_tmp[j] = tmp1 + (tmp2<<4);
            func2_tmp[j] = func2_tmp[j] ^ func2_key[j];
        }
        byte_to_bit(func2_tmp,func2_bit_tmp1, DATA_SIZE * 8);
        PERMUTATE_FUNC(func2_bit_tmp1,func2_bit_tmp2);
        bit_to_byte(func2_bit_tmp2, func2_tmp, DATA_SIZE * 8);
    }
    out[0]=func2_tmp[0];
    out[1]=func2_tmp[1];
    out[2]=func2_tmp[2];
    out[3]=func2_tmp[3];
}

u8 Matching(u8 *in1, u8 *in2)
{
    int i;
    u8 flag = 1;

    for (i = 0; i < 8; i++)
    {
        if (in1[i] != in2[i])
        {
            flag = 0;
            return flag;
        }
    }

    return flag;
}

u8 Matching_4bit(u8 *in1, u8 *in2)
{
    int i;
    u8 flag = 1;

    for (i = 0; i < 4; i++)
    {
        if (in1[i] != in2[i])
        {
            flag = 0;
            return flag;
        }
    }

    return flag;
}

void int_to_char(u32 in, u8 *out)
{
    int i = 0;

    out[0] = in % 10;
    out[1] = (in % 100) / 10;
    out[2] = (in % 1000) / 100;
    out[3] = (in % 10000) / 1000;
    out[4] = (in % 100000) / 10000;
    out[5] = (in % 1000000) / 100000;
    out[6] = (in % 10000000) / 1000000;
    out[7] = (in % 100000000) / 10000000;

    for (i = 0; i < 8; i++)
    {
        out[i] = out[i] + 48;
    }
}

void int_to_char_4bit(u32 in, u8 *out)
{
    int i = 0;

    out[0] = in % 10;
    out[1] = (in % 100) / 10;
    out[2] = (in % 1000) / 100;
    out[3] = (in % 10000) / 1000;

    for (i = 0; i < 4; i++)
    {
        out[i] = out[i] + 48;
    }
}

u8 Cracking(u32 init_int, u8 *password, u8 *output, u8 *answer)
{
    static u8 check1 = 0;
    static u8 check2 = 0;
    static u8 check3 = 0;

    if (check1 == 0)
    {
        int_to_char(init_int, password);
        Func1(password, output);
        Func2(&password[4], &output[4]);
        check1 = Matching(output, answer);

        return check1;
    }
    else if (check2 == 0)
    {
        int_to_char_4bit(init_int, password);
        Func1(password, output);
        check2 = Matching_4bit(output, answer);

        return check2;
    }
    else if (check3 == 0)
    {
        int_to_char_4bit(init_int, password);
        Func2(password, output);
        check3 = Matching_4bit(output, answer);

        return check3;
    }

}

void setup() {
    Serial.begin(9600); // open the serial port at 9600 bps:
    pinMode(LED_BUILTIN, OUTPUT);

    u8 password[8]= {0,};
    u8 output[8] = {0,};
    u8 answer_test[8] = {0x26, 0xce, 0x59, 0x80, 0x98, 0x73, 0x64, 0x16};
    u32 init_int = 12345678;
    u32 i, j=0;
    u8 check=0;

    Serial.println("-----------------");
    Serial.println(" TEST VECTOR ");
    Serial.println("-----------------");

    //TEST VECTOR
    check = Cracking(init_int, password, output, answer_test);

    if(check){
        Serial.println(">> CORRECT");
    }else{
        Serial.println(">> WRONG");
    }

    // Warning: This is example. This test vector will be changed in evaluation.
    // password range: 00000000 ~ 99999999
    u8 answer_bench[8] = {0x2b, 0x46, 0x9d, 0x42, 0x7b, 0x8f, 0x11, 0x9e};

    Serial.println("-----------------");
    Serial.println(" BENCHMARK ");
    Serial.println("-----------------");

    u32 time1;
    u32 time2;
    
    time1 = millis();
    init_int = 0;
    for (i = 0; i < 10000; i++)
    {
        check = Cracking(i, password, output, answer_bench);

        if (check)
        {
            break;
        }

        for (j = 0; j < 4; j++)
        {
            output[j] = 0;
        }

        init_int += 1;
    }

    for (i = 0; i < 10000; i++)
    {
        check = Cracking(i, password, output, &answer_bench[4]);

        if (check)
        {
            Serial.print("Answer is ");
            Serial.println(i * 10000 + init_int);

            break;
        }

        for (j = 0; j < 4; j++)
        {
            output[j] = 0;
        }
    }
    time2 = millis();

    Serial.print(">> ");
    Serial.println((time2-time1));
    Serial.println("-----------------");
}

void loop() { }
