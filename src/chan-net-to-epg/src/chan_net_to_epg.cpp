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
 *  - GB_MQ_HOST : ip of RabbitMQ
 *  - GB_MQ_USER : user
 *  - GB_MQ_PASS : pass
 *  - GB_MQ_EPG_QUEUE : epg queue
 *  - EPG_SOURCE_TYPE: 'dvb', 'xml', ''
 *  - EPG_SOURCE_URL: url of mpts
 *
 * */
int main(int argc, char *argv[])
{
    Lisence lic;

    Util::init();
    gst_mpegts_initialize();                                                                                   

    const char* mq_host  = getenv("GB_MQ_HOST");
    const char* mq_user  = getenv("GB_MQ_USER");
    const char* mq_pass  = getenv("GB_MQ_PASS");
    const char* mq_epg_queue  = getenv("GB_MQ_EPG_QUEUE");
    const char* epg_source_type = getenv("EPG_SOURCE_TYPE");
    const char* epg_source_url = getenv("EPG_SOURCE_URL");

    if(!mq_host || !epg_source_url || 
            !mq_user || !mq_pass || 
            !epg_source_type || !mq_epg_queue){
        LOG(error) << "Please set environment vars:" 
                   << "GB_MQ_HOST, GB_MQ_EPG_QUEUE, EPG_SOURCE_TYPE, EPG_SOURCE_TYPE\n";
        return EXIT_FAILURE;
    }
    MqProducer mq(mq_epg_queue, mq_host, 5672, mq_user, mq_pass);        
    LOG(info) << "Connect to MQ host " << mq_host << " queue " << mq_epg_queue;
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
    LOG(error) << "EXIT!";
}

