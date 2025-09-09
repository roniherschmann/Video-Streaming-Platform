#Author Roni Herschmann rlh2177
import socket
import sys
import os

#versiin 401
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for receiving requests from the client and 
#             sending the requested file back to the client
# Final Version 001

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <listen.port>")
        sys.exit(1)
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:
        print(f"Error creating socket: {e}")
        sys.exit(1)

    server_ip = '127.0.0.1'
    server_port = int(sys.argv[1])
    
    try:
        server_socket.bind((server_ip, server_port))
        server_socket.listen(5)  
        print(f"Server listening on {server_ip}:{server_port}")
    except Exception as e:
        print(f"Error binding or listening: {e}")
        sys.exit(1)
    
    # max chunk 
    chunksize = 1024 * 1024  

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection incoming: {client_address[0]}:{client_address[1]}")
        except Exception as e:
            print(f"Error accepting connection: {e}")
            continue

   
        handle_client(client_socket)


def handle_client(client_socket):
    """
    Handle all requests from a single client connection
    """
    while True:
        try:
            request = client_socket.recv(1024).decode().strip()
            if not request:
                print("Empty request received, closing connection")
                client_socket.close()
                break
                
            print(f"Received Request: '{request}'")
        except Exception as e:
            print(f"Error receiving request: {e}")
            client_socket.close()
            break

        # manifest request
        if request.endswith("_manifest"):
            video_name = request[:-len("_manifest")]
            manifestPath = f"./data/{video_name}/manifest.mpd"
            print(f"Manifest request for video '{video_name}', looking for file: {manifestPath}")
            try:
                with open(manifestPath, 'r') as m:
                    contentManifest = m.read().strip()
                client_socket.sendall((contentManifest + "\n").encode())
                print(f"Manifest for '{video_name}' sent successfully.")
            except FileNotFoundError:
                client_socket.sendall("Video not found\n".encode())
                print(f"Manifest file not found at {manifestPath}")
            except Exception as e:
                print(f"Error sending manifest: {e}")
                client_socket.close()
                break
            continue

        
        parts = request.split('_')
        
        if len(parts) >= 3:
            try:
                video_name = parts[0]
                bitrate = parts[1]
                chunk_number = int(parts[2])
                
                chunk_filename = f"./data/{video_name}/chunks/{video_name}_{bitrate}_{chunk_number:05d}.m4s"
                print(f"Requested chunk: {chunk_filename}")
                
                if not os.path.exists(chunk_filename):
                    print(f"Chunk file not found: {chunk_filename}")
                    client_socket.sendall((0).to_bytes(4, byteorder='big'))
                    continue
                
                # GET file size
                file_size = os.path.getsize(chunk_filename)
                print(f"Chunk file size: {file_size} bytes")
                
                # CHUNK SEND
                try:
                    with open(chunk_filename, 'rb') as file:
                        file_data = file.read()
                        
                        client_socket.sendall(len(file_data).to_bytes(4, byteorder='big'))
                        
                        client_socket.sendall(file_data)
                        print(f"Successfully sent chunk {chunk_filename}, size {len(file_data)} bytes")
                except Exception as e:
                    print(f"Error sending chunk: {e}")
                    client_socket.close()
                    break
            except Exception as e:
                print(f"Error processing chunk request: {e}")
                client_socket.sendall((0).to_bytes(4, byteorder='big'))
        else:
            print(f"Invalid chunk request format: {request}")
            client_socket.sendall((0).to_bytes(4, byteorder='big'))


if __name__ == "__main__":
    main()