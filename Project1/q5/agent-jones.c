#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

#define BUFSIZE 7680

unsigned int magic(unsigned int i, unsigned int j)
{
  i ^= j << 3;
  j ^= i << 3;
  i |= 58623;
  j %= 0x42;
  return i & j;
}

void error(const char *msg)
{
  fprintf(stderr, "error: %s\n", msg);
  exit(1);
}

size_t io(int socket, size_t n, char *buf)
{
  recv(socket, buf, n << 3, MSG_WAITALL);
  size_t i = 0;
  while (buf[i] && buf[i] != '\n' && i < n)
    buf[i++] ^= 0x42;
  return i;
}

void handle(int client)
{
  char buf[BUFSIZE];
  memset(buf, 0, sizeof(buf));
  io(client, BUFSIZE, buf);
}

int main(int argc, char *argv[])
{
  if (argc != 2)
  {
    fprintf(stderr, "usage: %s port\n", argv[0]);
    return 1;
  }

  int srv = socket(AF_INET, SOCK_STREAM, 0);
  if (srv < 0)
    error("socket()");

  int on = 1;
  if (setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) < 0)
    error("setting SO_REUSEADDR failed");

  struct sockaddr_in server, client;
  memset(&server, 0, sizeof(server));
  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_port = htons(atoi(argv[1]));

  if (bind(srv, (struct sockaddr *) &server, sizeof(server)) < 0)
    error("bind()");

  if (listen(srv, 5) < 0)
    error("listen()");

  socklen_t c = sizeof(client);
  int client_socket;
  for (;;)
  {
    if ((client_socket = accept(srv, (struct sockaddr *) &client, &c)) < 0)
      error("accept()");
    handle(client_socket);
    close(client_socket);
  }

  return 0;
}