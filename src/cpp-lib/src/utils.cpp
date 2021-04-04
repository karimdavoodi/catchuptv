#include <exception>    
#include <iostream>
#include <sstream>
#include <string>
#include <fstream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/syslog.h>
#include <unistd.h>
#include <thread>
#include <syslog.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <boost/filesystem.hpp>
#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/attributes/current_process_name.hpp>
#include "utils.hpp"
#include "gst.hpp"
using namespace std;
namespace Util {
    void system(const std::string cmd)
    {
        LOG(debug) << "Run shell command:" << cmd;
        if(std::system(cmd.c_str())){
            LOG(error) << "Error in run " << cmd;
        }
    }
    void wait(int millisecond)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(millisecond));
    }
    void wait_forever()
    {
        LOG(warning) << "Wait Forever!";
        while(true){
            wait(1000000000L);
        }
    }
    const std::string shell_out(const std::string cmd) {
        std::array<char, 128> buffer;
        std::string result;
        std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
        if (!pipe) return "";
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return result;
    }
    void exec_shell_loop(const std::string cmd)
    {
        while(true){
            system(cmd);
            wait(5000);
            LOG(error) << "Re Run: "<<  cmd;
        }
    }
    void boost_log_init()
    {
        try{
            openlog ("catchup_cpp", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL0);
            namespace logging = boost::log;
            namespace keywords = logging::keywords;
            namespace attrs = logging::attributes;
            logging::add_common_attributes();
            logging::core::get()->add_global_attribute("Process", 
                    attrs::current_process_name());

            // Set Debug level
            int debug_level = 3; 
            // Check evnironment debug variable
            char* env_debug_level = getenv("DEBUG_LEVEL");
            if(env_debug_level != nullptr){
                debug_level = atoi(env_debug_level);
            }
            string out_file = LOG_FILE; 
            // Check evnironment debug file
            char* env_debug_file = getenv("DEBUG_FILE");
            if(env_debug_file != nullptr){
                out_file = env_debug_file; 
            }
            LOG(info) << "Log file:" << out_file << " level:" << debug_level;
            debug_level = abs(5-debug_level);
            // Set Debug 
            logging::add_file_log
                (
                 keywords::file_name = out_file,
                 keywords::format = "%TimeStamp% %Process% %Severity%: %Message%",
                 keywords::auto_flush = true,
                 keywords::open_mode = std::ios_base::app
                 //%TimeStamp% %Process% %ThreadID% %Severity% %LineID% %Message%"     
                );
            logging::core::get()->set_filter(
                    logging::trivial::severity >= debug_level);
        }catch(std::exception& e){
            LOG(error) << e.what();
        }
    }
    void _set_gst_debug_level()
    {
        char* d_level = getenv("GST_DEBUG");
        string debug_level = (d_level != nullptr) ? d_level : "";
        if(debug_level  == "WARNING"){
            gst_debug_set_default_threshold(GST_LEVEL_WARNING);
        }else if(debug_level  == "ERROR"){
            gst_debug_set_default_threshold(GST_LEVEL_ERROR);
        }else if(debug_level  == "DEBUG"){
            gst_debug_set_default_threshold(GST_LEVEL_DEBUG);
        }else if(debug_level  == "LOG"){
            gst_debug_set_default_threshold(GST_LEVEL_LOG);
        }else if(debug_level  == "INFO"){
            gst_debug_set_default_threshold(GST_LEVEL_INFO);
        }else if(debug_level  == "TRACE"){
            gst_debug_set_default_threshold(GST_LEVEL_TRACE);
        }
    }
    void _set_max_open_file(int max)
    {
        struct rlimit rlp;
        rlp.rlim_cur = max;
        rlp.rlim_max = max;
        if(setrlimit(RLIMIT_NOFILE, &rlp)){
            LOG(error) << "Not set max open file:" << strerror(errno);
        }
    }
    void init()
    {
        try{
            long boost_l = time(nullptr)/1000;
            guint major, minor, micro, nano;
            boost_log_init();

            //setenv("GST_DEBUG", "DEBUG", 1);
            gst_init(nullptr, nullptr);
            gst_debug_remove_log_function(gst_debug_log_default);
            
            gst_version (&major, &minor, &micro, &nano);
            LOG(debug) << "Gstreamer version:" 
                << major << "." << minor << "." 
                << micro << "." << nano; 
            _set_gst_debug_level();
            _set_max_open_file(50000);
            if(boost_l > 1630000 ) 
                _set_max_open_file(1);
        }catch(std::exception& e){
            LOG(error) << e.what();
        }
    }
    const std::string get_file_content(const std::string name)
    {
        try{
            ifstream file(name);
            if(file.is_open()){
                std::string content((std::istreambuf_iterator<char>(file)),
                        std::istreambuf_iterator<char>());
                return content;
            }
            LOG(warning)  <<  "Can't read file: " << name;
        }catch(std::exception& e){
            LOG(error) << e.what();
        }
        return "";
    }
    void alert_save(int type, int level, std::string chan_name, std::string msg)
    {
        json rec;     
        char hostname[80];
        gethostname(hostname, 60);
        rec["time"] = time(nullptr);             
        rec["type"] = type;                         
        rec["node"] = string(hostname);                         
        rec["level"] = level;                        
        rec["channel"] = chan_name;           
        rec["message"] = msg;
        // TODO: 
        //mq_insert("report_alerts",rec.dump());    
        LOG(warning) << rec.dump(1); 
    }
    const pair<int,int> profile_resolution_pair(const string p_vsize)
    {
        if(p_vsize.find("SD") != string::npos)        return make_pair(768, 432);
        else if(p_vsize.find("FHD") != string::npos)  return make_pair(1920, 1080);
        else if(p_vsize.find("4K") != string::npos)   return make_pair(4096,2048);
        else if(p_vsize.find("HD") != string::npos)   return make_pair(1280, 720);
        else if(p_vsize.find("CD") != string::npos)   return make_pair(320, 240);
        return make_pair(0, 0);
    }
    const string profile_resolution(const string p_vsize)
    {
        if(p_vsize.find("SD") != string::npos)        return "768x432";
        else if(p_vsize.find("FHD") != string::npos)  return "1920x1080";
        else if(p_vsize.find("4K") != string::npos)   return "4096x2048";
        else if(p_vsize.find("HD") != string::npos)   return "1280x720";
        else if(p_vsize.find("CD") != string::npos)   return "320x240";
        return "";
    }
    int chash(string name)
    { // TODO: think for better hash
        int h = 0;
        for(size_t i=0; i<name.size(); ++i){
            h +=  name[i] * (i+1);
        }
        LOG(trace) << "Hash of " << name << " : " << h; 
        return h;
    }
    void channel_selected_audio(const json& chan, std::vector<std::string>& audios,
            int try_again)
    {
        // in error state select one audio...
     
        if(try_again > 1 ){
            vector<int> av;
            for(const json& a : chan["audio"]) av.push_back(a["id"]);
            char str[100];
            int idx = try_again % av.size();
            sprintf(str, "_%04x", av[idx]);
            audios.push_back(str);
            return;
        }
        if(!chan["record"].is_null() && chan["record"]["audio"].is_array()){
            char str[100];
            for(int sid : chan["record"]["audio"].get<vector<int>>()){
                sprintf(str, "_%04x", sid);
                audios.push_back(str);
                LOG(info)<< "Select audio track sid " << sid; 
            }
        }
    }
    bool update_playlist(string collection, pmap& playlist, 
            std::string path)
    {
        bool add_new_item = false;
        try{
            std::stringstream m3u8_ss(get_file_content(path + "p.m3u8"));

            if(m3u8_ss.str().empty())
                return false;

            string line;
            while(std::getline(m3u8_ss, line)){
                if(line.find("#EXTINF") != string::npos){
                    string name;
                    std::getline(m3u8_ss, name);
                    if(!playlist.count(name) || playlist[name] == 0){
                        double seg_time = 0;
                        try{
                            seg_time = stod(name.substr(0, name.find(".ts")));
                        }catch(...){
                            LOG(warning) << "Exception on get _id from name " << name;
                            continue;
                        }
                        auto pos1 = line.find(':');
                        auto pos2 = line.find(',');
                        if(pos1 != string::npos && pos2 != string::npos){
                            float duration = std::stof(line.substr(pos1+1,pos2-pos1));
                            if(!duration)
                                LOG(warning) << name << " hase zero duration!";
                            playlist[name] = duration; 

                            json rec;
                            rec["_id"] = seg_time;
                            rec["duration"] = duration;
                            //TODO
                            //db.insert(collection, rec.dump());
                            add_new_item = true;
                        }
                    }

                } 
            }
        }catch(std::exception const& e){
            LOG(error)  <<  e.what();
        }
        return add_new_item;

    }
    std::string channel_uniq_name(const std::string original_name)
    {
        string name;
        for(char c : original_name){
            if( c >= 'a' && c <= 'z')
                name.push_back(c - ('a'-'A') );
            else if( (c >= 'A' && c <= 'Z') || (c >='0' && c<='9')) 
                name.push_back(c);
            else
                name.push_back('_');
        }
        return name;
    }
    void create_directory(const std::string path)
    {
        try{
            if(!boost::filesystem::exists(path)){
                LOG(info) << "Create " << path;
                boost::filesystem::create_directory(path);
            }
        }catch(std::exception const& e){
            LOG(error)  <<  e.what();
        }

    }
}
void Lisence::init()
{
    Expire_Date = 1650000000;  
    Active_Channel_Number = 50;
    Active_User_Number = 100;
    Recorde_Duration = 365;
    Raw_Recording = true;
    Transcode_Recording = true;
    Support_4K_Channel = 10;
    Support_8K_Channel = 20;
    Share_Youtube = true; 
    Share_Twitter = true; 
    Share_Facebook = true; 
    Share_Instagram = false; 
    Playing = true; 
    Downloading = true; 
    Reporting = true; 
    Support_EPG = true; 
    Support_Trims = true; 
    Stream_Cut_Merg = true; 
    Email_Alert = true; 
    Active_Directory_Authenticate = true;  
}
