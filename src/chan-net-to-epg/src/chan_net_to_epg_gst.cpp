#include <exception>
#include <ratio>
#include <thread>
#include <gst/mpegts/mpegts.h>
#include "gst/gstelement.h"
#include "../../cpp-lib/src/utils.hpp"
#include "../../cpp-lib/src/mq.hpp"
#include "../../cpp-lib/src/gst.hpp"
#define MIN_EPG_DURATION 200
using namespace std;

struct Event {
    int serviceId;
    string name;
    long start = 0;
    int duration = 0;
};
using epg_list =  map<long, Event>; 

struct Edata {
    Gst::Data d;
    map<int, epg_list> eit_db;
    long               day_epoch_base;
};

void queue_guard(GMainLoop* loop, GstElement* queue, int sec);
int bus_on_message(GstBus * /*bus*/, GstMessage * message, gpointer user_data);
void channel_epg_update(Edata& edata, MqProducer& mq);
void load_enums();
int init_data(Edata& edata);
/*
 *   The Gstreamer main function
 *   Convert udp:://in_multicast:port to HLS playlist 
 *   
 *   @param in_multicast : multicast of input stream
 *   @param port: output multicast port numper 
 *   @param hls_root: Path of HLS playlist
 *
 * */
void udp_to_epg(const char* mpts_url, MqProducer& mq)
{

    try{
        Edata edata;
        if(init_data(edata) == 0){
            LOG(warning) << "Not found active channel for " << mpts_url;
            return;
        }
        edata.d.loop      = g_main_loop_new(nullptr, false);
        edata.d.pipeline  = GST_PIPELINE(gst_element_factory_make("pipeline", nullptr));
        auto udpsrc     = Gst::add_element(edata.d.pipeline, "udpsrc"),
             queue      = Gst::add_element(edata.d.pipeline, "queue", "queue_src"),
             tsparse    = Gst::add_element(edata.d.pipeline, "tsparse"),
             fakesink   = Gst::add_element(edata.d.pipeline, "tsdemux");
        gst_element_link_many(udpsrc, queue, tsparse, fakesink, nullptr);

        g_object_set(udpsrc, "uri", mpts_url, nullptr);
        g_object_set(tsparse, "parse-private-sections", true, nullptr);

        load_enums();
        edata.d.bus = gst_pipeline_get_bus(edata.d.pipeline);
        edata.d.watch_id = gst_bus_add_watch(edata.d.bus, bus_on_message, &edata); 
        gst_element_set_state(GST_ELEMENT(edata.d.pipeline), GST_STATE_PLAYING);

        std::thread t([&](){
                    Util::wait(60000);
                    g_main_loop_quit(edata.d.loop);
                });
        
        g_main_loop_run(edata.d.loop);
        t.join();
        channel_epg_update(edata, mq);
    }catch(std::exception& e){
        LOG(error) << e.what();
    }
}
void load_enums()
{
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_TABLE_ID);
    g_type_class_ref (GST_TYPE_MPEGTS_RUNNING_STATUS);
    g_type_class_ref (GST_TYPE_MPEGTS_DESCRIPTOR_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_DESCRIPTOR_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_ATSC_DESCRIPTOR_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_ISDB_DESCRIPTOR_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_MISC_DESCRIPTOR_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_ISO639_AUDIO_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_SERVICE_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_TELETEXT_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_STREAM_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_DVB_TABLE_ID);
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_ATSC_TABLE_ID);
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_SCTE_TABLE_ID);
    g_type_class_ref (GST_TYPE_MPEGTS_MODULATION_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_CODE_RATE);
    g_type_class_ref (GST_TYPE_MPEGTS_CABLE_OUTER_FEC_SCHEME);
    g_type_class_ref (GST_TYPE_MPEGTS_TERRESTRIAL_TRANSMISSION_MODE);
    g_type_class_ref (GST_TYPE_MPEGTS_TERRESTRIAL_GUARD_INTERVAL);
    g_type_class_ref (GST_TYPE_MPEGTS_TERRESTRIAL_HIERARCHY);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_LINKAGE_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_DVB_LINKAGE_HAND_OVER_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_COMPONENT_STREAM_CONTENT);
    g_type_class_ref (GST_TYPE_MPEGTS_CONTENT_NIBBLE_HI);
    g_type_class_ref (GST_TYPE_MPEGTS_SCTE_STREAM_TYPE);
    g_type_class_ref (GST_TYPE_MPEGTS_SECTION_SCTE_TABLE_ID);
}
long gst_date_to_epoch(GstDateTime* date, Edata* edata)
{
    long n;
    n  = 3600 * gst_date_time_get_hour(date);
    n += 60 * gst_date_time_get_minute(date);
    n += gst_date_time_get_second(date);
    /*
       LOG(trace) << "tz:" << gst_date_time_get_time_zone_offset(date)
       << " iso " << gst_date_time_to_iso8601_string(date)
       << " base:" << day_epoch_base 
       << " time:" << day_epoch_base + n;
       */
    return  edata->day_epoch_base +  n + (3600*3);
}
void dump_descriptors (GstMpegtsEITEvent *event, int serviceId, Edata* edata)
{
    GPtrArray *descriptors = event->descriptors;
    for (int i = 0; i < (int)descriptors->len; i++) {
        auto* desc = (GstMpegtsDescriptor *)
            g_ptr_array_index (descriptors, i);
        
        if(desc->tag == GST_MTS_DESC_DVB_SHORT_EVENT) {
            gchar *language_code, *event_name, *text;
            if (gst_mpegts_descriptor_parse_dvb_short_event (
                        desc, 
                        &language_code,
                        &event_name, 
                        &text)) {
                Event e;
                e.serviceId = serviceId; 
                
                e.start = gst_date_to_epoch(event->start_time, edata);            
                e.duration = event->duration;
                e.name = event_name; 
                edata->eit_db[serviceId][e.start] = e;
                /*
                LOG(error) << "EPG1: " << serviceId 
                        << ": " << event->running_status
                        << ": " << e.start
                        << ": " << e.duration 
                        << ": " << e.name;
                */
                g_free (language_code);
                g_free (event_name);
                g_free (text);
            }
        }else{
            //LOG(info) << " Not shor event " << event->start_time;
        }
    }
}
void save_eit(GstMpegtsSection *sec, Edata *edata)
{
    const GstMpegtsEIT *eit = gst_mpegts_section_get_eit(sec);
    if(eit == nullptr){
        LOG(warning) << "Can't parse mpegts EIT";
        return;
    } 

    int len = eit->events->len;
    /*
       LOG(debug) << "EIT: "
       << " section_id " << sec->subtable_extension
       << " event number:" << len;
       */
    /*
       << " transport_stream_id " << eit->transport_stream_id
       << " original_network_id " << eit->original_network_id
       << " segment_last_section_number " << eit->segment_last_section_number
       << " last_table_id " << eit->last_table_id
       << " actual_stream " << (eit->actual_stream ? "true" : "false") 
       << " present_following " << (eit->present_following ? "TRUE" : "FALSE");
       */
    for (int i = 0; i < len; i++) {
        auto *event = (GstMpegtsEITEvent *)
            g_ptr_array_index(eit->events, i);
        if(event->running_status == 0) continue;
        dump_descriptors(event, sec->subtable_extension, edata);
    }
    //g_object_unref(GST_OBJECT(eit));

}
int bus_on_message(GstBus * /*bus*/, GstMessage * message, gpointer user_data)
{
    auto edata = (Edata *) user_data;

    switch (GST_MESSAGE_TYPE (message)) {
        case GST_MESSAGE_ELEMENT:
            {
                GstMpegtsSection *section;
                if((section = gst_message_parse_mpegts_section (message))) {
                    if(GST_MPEGTS_SECTION_TYPE (section) == GST_MPEGTS_SECTION_EIT) {
                        save_eit(section, edata); 
                    }
                    gst_mpegts_section_unref (section);
                }
                break;
            }
        case GST_MESSAGE_ERROR:
            {
                gchar *debug;
                GError *err;
                gst_message_parse_error (message, &err, &debug);
                LOG(warning) <<  err->message << " debug:" << debug;
                g_error_free (err);
                g_free (debug);
                g_main_loop_quit (edata->d.loop);
                break;
            }
        case GST_MESSAGE_EOS:
            LOG(error) <<  "Got EOS";    
            g_main_loop_quit(edata->d.loop);
            break;
        default: ;
    }
    return true;
}
void channel_epg_update(Edata& edata, MqProducer& mq)
{
    int add_to_db = 0;
    if(!edata.eit_db.empty()){
        json filter = json::object();
        long now = time(nullptr);
        filter["channelId"] = 0;
        filter["programStart"] = 0;
        for(const auto& [serviceId, epgs] : edata.eit_db){
            for(const auto& [start, epg] : epgs){
                if(start < now - 20*3600 ){
                    LOG(trace) << "Ignore last EPG start " << start;
                    continue;
                } 
                if(epg.duration < MIN_EPG_DURATION){
                    LOG(trace) << "EPG is short, Ignor this: " << epg.name;
                    continue;
                } 
                LOG(debug) << "EPG for chan " 
                    << " serviceId " << serviceId 
                    << " Start " << epg.start 
                    << " Duration " << epg.duration 
                    << " Title " << epg.name;
                json rec = json::object();
                rec["channelSid"] = serviceId;
                rec["channel"] = ""; // TODO: find channel name 
                rec["programName"] = epg.name;
                rec["programStart"] = epg.start;
                rec["programEnd"] =  epg.start + epg.duration;
                mq.send(rec.dump());
                Util::wait(20);
                add_to_db++;
            }
        }
    }
    LOG(info) << "EPG number that add to DB:" << add_to_db;

}
int init_data(Edata& edata)
{
    time_t now = time(nullptr);
    struct tm *now_t = localtime(&now);
    edata.day_epoch_base = now - (now_t->tm_hour*3600 + now_t->tm_min*60 + now_t->tm_sec);
    LOG(trace) << "Day base is " << edata.day_epoch_base;
    edata.eit_db.clear();
    return 0; 
}
