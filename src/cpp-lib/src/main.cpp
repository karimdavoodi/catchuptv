#include <time.h>
#include "mq.hpp"

int main()
{
    
    MqProducer mq7("logx7");
    while(1){
        mq7.send("Hello ...");
        mq7.send_segment_info("TRT1", 161231234.123, 5.12345);
        mq7.send_segment_file("TRT1", "/tmp/1.ts", 161231234.123);
    }
}
