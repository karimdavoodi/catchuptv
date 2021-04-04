#include <cctype>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <vector>
#include <thread>
#include <boost/format.hpp>
#include <gst/mpegts/mpegts.h>
#include <boost/log/trivial.hpp>
#include "../../cpp-lib/src/utils.hpp"
#include "../../cpp-lib/src/mq.hpp"
using namespace std;

void udp_to_epg(const char* mpts_url, MqProducer& mq);
/*
 * ENV vars:
 *  - MQ_HOST : ip of RabbitMQ
 *  - MQ_USER : user
 *  - MQ_PASS : pass
 *  - MQ_EPG_EXCHANGE : epg exchange
 *  - EPG_SOURCE_TYPE: 'dvb', 'xml', ''
 *  - EPG_SOURCE_URL: url of mpts
 *
 * */
int main(int argc, char *argv[])
{
    Lisence lic;

    Util::init();
    gst_mpegts_initialize();                                                                                   

    const char* mq_host  = getenv("MQ_HOST");
    const char* mq_user  = getenv("MQ_USER");
    const char* mq_pass  = getenv("MQ_PASS");
    const char* mq_epg_exchange  = getenv("MQ_EPG_EXCHANGE");
    const char* epg_source_type = getenv("EPG_SOURCE_TYPE");
    const char* epg_source_url = getenv("EPG_SOURCE_URL");

    if(!mq_host || !epg_source_url || 
            !mq_user || !mq_pass || 
            !epg_source_type || !mq_epg_exchange){
        LOG(error) << "Please set environment vars:" 
                   << "MQ_HOST, MQ_EPG_EXCHANGE, EPG_SOURCE_TYPE, EPG_SOURCE_TYPE\n";
        return EXIT_FAILURE;
    }
    MqProducer mq(mq_epg_exchange, mq_host, 5672, mq_user, mq_pass);        
    if(!strcmp(epg_source_type, "dvb")){
        while(true){
            udp_to_epg(epg_source_url, mq);
            Util::wait(1000 * 30 * 60); 
        }
    }else if(!strcmp(epg_source_type, "xml")){
        LOG(error) << "TODO: not implement XML";
    }else{
        LOG(error) << "Invalid EPG source type " << epg_source_type;
    }
}

