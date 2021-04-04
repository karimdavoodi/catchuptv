
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <amqp.h>
#include <amqp_tcp_socket.h>


#define SUMMARY_EVERY_US 1000000

void die_on_amqp_error(amqp_rpc_reply_t x, char const *context) {
  switch (x.reply_type) {
    case AMQP_RESPONSE_NORMAL:
      return;
    default:
      fprintf(stderr, "Error %s\n", context);
  }
}
void die(char const *context) {
    fprintf(stderr, "error: %s\n", context);
    exit(1);
}
void die_on_error(int x, char const *context) {
  if (x < 0) {
    fprintf(stderr, "%s: %s\n", context, amqp_error_string2(x));
    exit(1);
  }
}
static void send_batch(amqp_connection_state_t conn, char const *exchange,
                       int message_count) {
  int i;
  int sent = 0;

  char message[256];
  amqp_bytes_t message_bytes;

  for (i = 0; i < (int)sizeof(message); i++) {
    message[i] = i & 0xff;
  }

  message_bytes.len = sizeof(message);
  message_bytes.bytes = message;

  for (i = 0; i < message_count; i++) {
    die_on_error(amqp_basic_publish(conn, 1, exchange,
                                    amqp_cstring_bytes(queue_name), 0, 0, NULL,
                                    message_bytes),
                 "Publishing");
    sent++;
  }
}

int main(int argc, char const *const *argv) {
  char const *hostname;
  char const *exchange;
  char const *exchangetype = "fanout";
  int port, status;
  int message_count;
  amqp_socket_t *socket = NULL;
  amqp_connection_state_t conn;

  if (argc < 4) {
    fprintf(stderr,
            "Usage: amqp_producer host port exchange  message_count\n");
    return 1;
  }

  hostname = argv[1];
  port = atoi(argv[2]);
  exchange = argv[3];
  message_count = atoi(argv[4]);

  conn = amqp_new_connection();

  socket = amqp_tcp_socket_new(conn);
  if (!socket) {
    die("creating TCP socket");
  }

  status = amqp_socket_open(socket, hostname, port);
  if (status) {
    die("opening TCP socket");
  }

  die_on_amqp_error(amqp_login(conn, "/", 0, 131072, 0, AMQP_SASL_METHOD_PLAIN,
              "guest", "guest"), "Logging in");
  amqp_channel_open(conn, 1);
  die_on_amqp_error(amqp_get_rpc_reply(conn), "Opening channel");
    
  amqp_exchange_declare(conn, 1, amqp_cstring_bytes(exchange),
                        amqp_cstring_bytes(exchangetype), 0, 0, 0, 0,
                        amqp_empty_table);
  die_on_amqp_error(amqp_get_rpc_reply(conn), "Declaring exchange");

  send_batch(conn, exchange,  message_count);

  die_on_amqp_error(amqp_channel_close(conn, 1, AMQP_REPLY_SUCCESS),
                    "Closing channel");
  die_on_amqp_error(amqp_connection_close(conn, AMQP_REPLY_SUCCESS),
                    "Closing connection");
  die_on_error(amqp_destroy_connection(conn), "Ending connection");
  return 0;
}
