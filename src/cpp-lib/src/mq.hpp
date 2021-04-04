#include<iostream>
#include "../third_party/SimpleAmqpClient/SimpleAmqpClient.h"
using namespace AmqpClient;

class MqProducer {
    private:
        AmqpClient::Channel::ptr_t conn = nullptr; 
        std::string queue; 
        std::string host; 
        int port;
        std::string username;
        std::string password; 
        std::string vhost; 
        int frame_max;
    public:
        MqProducer(
                const std::string &queue, 
                const std::string &host = "127.0.0.1", 
                int port = 5672, 
                const std::string &username = "guest", 
                const std::string &password = "guest", 
                const std::string &vhost = "/", 
                int frame_max = 10*1024*1024)
                : queue(queue),
                host(host),
                port(port),
                username(username),
                password(password),
                vhost(vhost),
                frame_max(frame_max){
                    connect();
                }
        bool connect();
        bool send(const std::string& msg);
        bool send_segment_file(
                const std::string channel_name, 
                const std::string filepath, 
                double start_time);
        bool send_segment_info(
                const std::string channel_name, 
                double start_time, double duration);
};
