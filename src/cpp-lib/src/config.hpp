#pragma once

#define LOG_FILE         "/dev/stderr"


#define ENABLE_BLACKUP 1 

#define SEGMENT_DURATION 5      // larger than 2 , EFFECT ON catchup_hls.py CODE
#define SEGMENT_COUNT 7 
#define SEGMENT_MAX_COUNT int(86400 / (SEGMENT_DURATION-2) )
//#define SEGMENT_PATTERN  "/%000000000.ts"
#define SEGMENT_PATTERN    "/%0000000000000.ts"

#define JSON_UPDATE_MSEC 4800  
#define DB_UPDATE_EVERY  10    // every 10*5 sec 
#define RETRY_FOR_QUIT   30    // exit if no change for 30*5 sec
#define CHANNEL_UPDATE_TIMEOUT (60*4)

#define ROOT_LOCAL_ORIGNAL     "/home/catchup/local/original"
#define ROOT_LOCAL_TRANSCODE   "/home/catchup/local/transcode"
#define ROOT_REMOTE_ORIGNAL    "/home/catchup/remote/original"
#define ROOT_REMOTE_TRANSCODE  "/home/catchup/remote/transcode"

#define DB_QUERY_SIZE  10
#define DB_NAME     "catchup"
#define DB_SERVER      "mongodb://main:main_3123@dbase,node1,node2,node3,node4,node5/catchup?replicaSet=rs0&serverSelectionTryOnce=false"
//#define DB_SERVER      "mongodb://main:main_3123@127.0.0.1:27017/catchup"


#define LOG(level) BOOST_LOG_TRIVIAL(level) << \
                    "\033[0;32m[" << __func__ << ":" <<__LINE__ << "]\033[0m "

#define DB_ERROR(db, level) Error(db, __FILE__, __func__, __LINE__, level)

#define ALERT_SYSTEM    1
#define ALERT_STORAGE   2
#define ALERT_AUTH      3
#define ALERT_TS        4
#define ALERT_CHANNEL   5
#define ALERT_INFO      1
#define ALERT_WARNING   2
#define ALERT_ERROR     3
