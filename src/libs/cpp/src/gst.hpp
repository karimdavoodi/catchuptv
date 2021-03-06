#pragma once
#include "config.hpp"
#include <iostream>
#include <gst/gst.h>
#include <boost/log/trivial.hpp>
#include <vector>
namespace Gst {
    struct Data{
        GMainLoop*      loop;
        GstPipeline*    pipeline;
        GstBus*         bus;
        guint           watch_id;
        bool            add_audio;
        std::vector<std::string> audio_sids;

        Data():loop(nullptr), pipeline(nullptr), bus(nullptr), watch_id(0),add_audio(false){}
        ~Data(){
            try{
                if(pipeline != nullptr){
                    gst_element_set_state(GST_ELEMENT(pipeline), GST_STATE_NULL);
                    gst_object_unref(pipeline);
                }
                if(bus != nullptr){
                    gst_object_unref(bus);
                }
                if(watch_id){
                    g_source_remove(watch_id);
                } 
                if(loop != nullptr){
                    g_main_loop_unref(loop);
                }
                bus = nullptr; pipeline = nullptr; loop = nullptr; watch_id = 0;
                BOOST_LOG_TRIVIAL(info) << "Clean pipeline";
            }catch(std::exception& e){
                LOG(error) << e.what();
            }
        }
    };
    void init();
    std::string element_name(GstElement* element);
    std::string pad_name(GstPad* element);
    std::string caps_string(GstCaps* caps);
    void pipeline_timeout(Data& d, int sec);
    void print_int_property_delay(GstElement* element, const char* attr, int seconds);
    void set_max_queue_time(GstElement* queue, int sec);
    std::string pad_caps_string(GstPad* pad);
    std::string pad_caps_type(GstPad* pad);
    void dot_file(const GstPipeline* pipeline, const std::string& name, int sec = 5);
    GstElement* add_element(GstPipeline* pipeline, const std::string& plugin,
            const std::string& name = "", bool stat_playing = false);
    bool pad_link_element_static(GstPad* pad, GstElement* element, const std::string& pad_name);
    bool pad_link_element_request(GstPad* pad, GstElement* element, const std::string& pad_name);
    bool add_bus_watch(Data& d);
    bool element_link_request(GstElement* src, const char* src_name, 
              GstElement* sink, const char* sink_name);
    GstElement* insert_parser(GstPipeline* pipeline, GstPad* pad);
    bool demux_pad_link_to_muxer(
            GstPipeline* pipeline,
            GstPad* pad,
            const std::string_view muxer_element_name,
            const std::string_view muxer_audio_pad_name,
            const std::string_view muxer_video_pad_name,
            bool queue_buffer_zero = true);
    void queue_guard(GMainLoop* loop, GstElement* queue, int sec);

}
