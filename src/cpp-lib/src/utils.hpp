#pragma once
#include <iostream>
#include <string>
#include <string_view>
#include <boost/log/trivial.hpp>
#include "../third_party/json.hpp"
#include "config.hpp"
#include "../third_party/SimpleAmqpClient/SimpleAmqpClient.h"
using namespace AmqpClient;

using nlohmann::json;
using pmap = std::map<std::string, float>;
struct Audio {
    int id;
    std::string lang;
    std::string type;
};
struct Programs {
    std::string name;
    int serviceId;
    std::pair<int,std::string> video;
    std::vector< Audio > audio;
    int pcr_pid;
    bool scrambled;
    bool reserved;
    Programs():serviceId(0),video({0,""}),scrambled(false),reserved(false){}
};
struct Mpts {
    std::string name;
    int netId;
    int tsId;
    std::vector<Programs> programs;
    Mpts():netId(0),tsId(0){}
};

namespace Util {
    
    void wait_forever();
    void create_directory(const std::string path);
    void system(const std::string cmd);
    void wait(int millisecond);
    void boost_log_init();
    const std::string shell_out(const std::string cmd);
    void exec_shell_loop(const std::string cmd);
    void init();
    const std::pair<int,int> profile_resolution_pair(const std::string p_vsize);
    const std::string profile_resolution(const std::string p_vsize);
    void alert_save(int type, int level, std::string chan_name, std::string msg);
    std::string channel_uniq_name(const std::string original_name);
    void load_old_playlist(pmap& playlist, std::string path);
    bool update_playlist(std::string collection, pmap& playlist, std::string path);
    json get_my_channels(int node_id_num);
    void channel_selected_audio(const json& chan, std::vector<std::string>& audios,
            int try_transcode = 0);
}

class Lisence {
    public:
        long Expire_Date;
        int  Active_Channel_Number;
        int  Active_User_Number;
        int  Recorde_Duration;
        bool Raw_Recording;
        bool Transcode_Recording;
        bool Support_4K_Channel;
        bool Support_8K_Channel;
        bool Share_Youtube; 
        bool Share_Twitter; 
        bool Share_Facebook; 
        bool Share_Instagram; 
        bool Playing; 
        bool Downloading; 
        bool Reporting; 
        bool Support_EPG; 
        bool Support_Trims; 
        bool Stream_Cut_Merg; 
        bool Email_Alert; 
        bool Active_Directory_Authenticate;  

        Lisence(){ init(); } 
        void init();
};

/*
 *  Update json every 5 sec
 *  Update DB   every 50 sec
 *  Exit if no Update for 150 sec
 *
 *  Get channel by Other if no Update for 600 sec
 *
 */
#define THREADS_PLAYLIST_AND_DAY_REMAIN                                     \
    bool thread_running = true;                                         \
    std::thread playlist_th([&](){                                      \
            Mongo db;                                                   \
            pmap  playlist;                                             \
            long chan_id = chan["_id"];                                 \
            string chan_name = Util::channel_uniq_name(chan["name"]);   \
            string collection = "channel_" + chan_name + (is_record? "_ORG":"_PRX");\
            string msg = string("Start ")+(is_record? "record":"transcode")+" content"; \
            Util::alert_save(db, ALERT_CHANNEL, ALERT_INFO,chan["name"],msg);       \
            Util::wait(5000);                                           \
            int no_update = 0;                                          \
            int db_update = 0;                                          \
            long last_update = 0;                                       \
            while(thread_running){                                      \
            for(int i=0; thread_running && i<5; ++i)                \
            Util::wait(990);                                    \
            try{                                                    \
            if(Util::update_playlist(db, collection, playlist, hls_root)){  \
            no_update = 0;                                      \
            if(++db_update == DB_UPDATE_EVERY){                 \
            db_update = 0;                                  \
            string field = is_record?"updateRec":"updateTrc";   \
                if(!owner){                                     \
                    json chan = json::parse(                    \
                            db.find_id("config_channels", chan_id));    \
                    if(last_update && chan[field] != last_update){      \
                        LOG(warning) << "Exit backup mode of channel " \
                        << chan["name"].get<string>() << " Quit!"; \
                        thread_running = false;                         \
                        break;                                          \
                    }                                                   \
                }                                                   \
                last_update = time(nullptr);                        \
                string now = to_string(last_update);                \
                db.update_id("config_channels", chan_id,            \
                        "{\"" + field + "\": " + now +              \
                        ",\"update\": " + now + " }");              \
            }                                                   \
            }else{                                                      \
                if(++no_update == RETRY_FOR_QUIT){                      \
                    string msg = string("Can't ")+(is_record? "record":"transcode")+" content"; \
                    Util::alert_save(db, ALERT_CHANNEL, ALERT_ERROR, chan["name"],msg);\
                    thread_running = false;                             \
                    break;                                              \
                }                                                       \
            }                                                           \
            }catch(...){}                                           \
            }                                                           \
    });                                                         \
    Gst::add_bus_watch(d);                                              \
    gst_element_set_state(GST_ELEMENT(d.pipeline), GST_STATE_PLAYING);  \
    g_main_loop_run(d.loop);                                            \
    thread_running = false;                                             \
    playlist_th.join();                                                 \
    LOG(warning) << "Exit from " << chan["name"] << " Try" << try_again; 



