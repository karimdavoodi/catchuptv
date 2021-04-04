#pragma once
#include <iostream>
#include <mutex>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include "config.hpp"

class Mongo {
    private:
        mongocxx::client client{mongocxx::uri{DB_SERVER}};
        mongocxx::database db;
    public:
        Mongo():client{mongocxx::uri{DB_SERVER}}
                { db = client[DB_NAME]; }
        long count(const std::string& col, const std::string& filter);
        bool exists(const std::string& col, const std::string& filter);
        bool exists_id(const std::string& col, int64_t id);
        bool insert(const std::string& col, const std::string& filter);
        bool update_id(const std::string& col, int64_t id, const std::string& doc);
        bool remove_mony(const std::string& col, const std::string& filter);
        bool remove_id(const std::string& col, int64_t id);
        bool replace_id(const std::string& col, int64_t id,
                const std::string& doc);
        bool insert_or_replace_id(const std::string& col, int64_t id,
                const std::string& doc);
        bool replace(const std::string& col, const std::string& filter,
                const std::string& doc);
        bool insert_or_replace_filter(const std::string& col, const std::string& filter,
                                            const std::string& doc);
        int64_t get_uniq_id();
        std::string find_one_update(const std::string& col, 
                const std::string& filter, const std::string& doc);
        std::string find_one(const std::string& col, const std::string& filter);
        std::string find_mony(const std::string& col, const std::string& filter);
        std::string find_id(const std::string& col, int64_t id);
        std::string find_range(const std::string& col,
                long begin = 0, long end = DB_QUERY_SIZE);
        std::string find_filter_range(const std::string& col,
                const std::string& filter,
                long begin = 0, long end = DB_QUERY_SIZE);
        void info();
};
