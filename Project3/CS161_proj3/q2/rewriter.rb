#!/usr/bin/ruby

def manipulate(client_ip,client_port,server_ip,server_port,http_request)
  http_request["false"] = "true"
  http_request["181"] = "180"
  return http_request
end

################################################################################
############### Under no circumstances, EVER, should you #######################
############### need to modify anything below this line  #######################
################################################################################

require 'socket'
require 'ipaddr'

class UNIXSocket
  def meta=(meta)
    @meta=meta
  end
  
  def meta
    @meta
  end
end

SOCK="/tmp/pysslsniff.sock"

begin
  File.unlink(SOCK)
rescue
end

serv=UNIXServer.open(SOCK)
fds=[serv]

while fds.length
    selres=select(fds,[],fds)
    
    # Selected for read
    selres[0].each { |fd|
      if fd==serv then
        # Read on a server means accept
        con=serv.accept
        con.meta=con.recv(12).unpack('LSLS')
        con.meta[0]=IPAddr::ntop([con.meta[0]].pack('N')).to_s
        con.meta[2]=IPAddr::ntop([con.meta[2]].pack('N')).to_s
        fds.push con
      else
        # Data ready!
        begin
          # Read it
          l=fd.recv(4).unpack('L')[0]
          r=fd.recv(l)
          # Manipulate
          r=manipulate(*fd.meta,r)
          # Return it
          fd.send([r.length].pack('L'),0)
          fd.send(r,0)
        rescue
          # It probably closed on us, get rid of it
          fd.close
          fds.delete fd
        end
      end
    }
    
    # Selected for error
    selres[2].each { |fd|
      if fd==serv then
        # Error on server => let's exit
        fds.each { |ifd| ifd.close }
        break
      else
        # It probably closed on us, get rid of it
        fds.delete fd
        fd.close
      end
    }
end
