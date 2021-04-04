#include <iostream>
#include <string>
#include <fstream>
#include <boost/filesystem.hpp>
#include <boost/log/trivial.hpp>
#include "../third_party/json.hpp"
#include "config.hpp"
#include "mq.hpp"
using namespace std;

bool MqProducer::connect()
{
    try{
        conn = AmqpClient::Channel::Create(host, port, username, password, vhost, frame_max);
        //conn->DeclareExchange(exchange, Channel::EXCHANGE_TYPE_FANOUT);
        conn->DeclareQueue(queue);
        LOG(info) << "Connect to MQ, "
            << " Host:" << host
            << " Queue:" << queue;
    }catch(std::exception& e){
        LOG(error) << e.what();
        return false;
    }
    return true;
}
bool MqProducer::send_segment_file(
        const string channel_name, 
        const string filepath, 
        double start_time)
{
    string data = string("{") +
        "\"channel_name\":\"" + channel_name + "\" " +
        ",\"start_time\":" + to_string(start_time) +
        "}"; 
    if(data.size() > 250){
        LOG(error) << "Channel name is long! ";
        return false;
    }
    for(size_t i=data.size(); i<255; ++i){
        data.push_back(' ');
    }

    ifstream in(filepath);
    if(!in.is_open()){
        LOG(error) << "Can't open " << filepath;
        return false;
    }
    char buf[4096];
    int n;
    while( (n = in.readsome(buf, 4096)) ){
        for(int i=0; i<n; ++i){
            data.push_back(buf[i]);
        }
    }
    send(data);

    return true;
}
bool MqProducer::send_segment_info(
        const string channel_name, 
        double start_time, double duration)
{
    string json = string("{") +
        "\"channel_name\":\"" + channel_name + "\" " +
        ",\"start_time\":" + to_string(start_time) +
        ",\"duration\":" + to_string(duration) +
        "}"; 

    return send(json);
}
bool MqProducer::send(const std::string& msg)
{
    try{
        BasicMessage::ptr_t message = BasicMessage::Create(msg);
        conn->BasicPublish("", queue, message);

        LOG(info) << "Sent msg len " << msg.size();
        return true;
    }catch(MessageRejectedException& e){
        LOG(error) << "MessageRejectedException: " << e.what();
    }catch(MessageReturnedException& e){
        LOG(error) << "MessageRejectedException: " << e.what();
    }catch(ConsumerTagNotFoundException& e){
        LOG(error) << "MessageRejectedException: " << e.what();
    }catch(ConsumerCancelledException& e){
        LOG(error) << "MessageRejectedException: " << e.what();
    }catch(ConnectionClosedException& e){
        connect();
        LOG(error) << "Closed connection, try to connect again, " << e.what();
    }catch(std::exception& e){
        connect();
        LOG(error) << "Error. try to connect again, " << e.what();
    }
    return false;
}
