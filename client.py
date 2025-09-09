# Author: Roni Herschmann rlh2177
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# client.py - the client program for sending request to the server and 
#             playing the received video chunks
# Final Version 17

import xml.etree.ElementTree as ET
import threading
from queue import Queue
#from video_player import play_chunks
import sys
import time
import os
import socket

connection_socket = None

def safe_close_socket():
    global connection_socket
    if connection_socket:
        try:
            connection_socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print(f"Error during socket shutdown: {e}")
        connection_socket.close()
        connection_socket = None

def get_manifest_and_chunks(server_addr, server_port, video_name, bitrate=None, chunk_index=None):
    global connection_socket
    
    if connection_socket is None:
        try:
            connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection_socket.connect((server_addr, server_port))
            print(f"Connected to {server_addr}:{server_port}")
        except Exception as e:
            print(f"Error creating connection: {e}")
            return None, None
    
    if bitrate is None and chunk_index is None:
        try:
            request_str = f"{video_name}_manifest\n"
            print(f"Sending manifest request: {request_str.strip()}")
            connection_socket.sendall(request_str.encode())
            response = connection_socket.recv(4096).decode().strip()
            return response, 0
        except Exception as e:
            print(f"Error getting manifest: {e}")
            safe_close_socket()
            return None, None
    
    # Request CHUNK
    try:
        request_str = f"{video_name}_{bitrate}_{chunk_index}\n"
        print(f"Sending chunk request: {request_str.strip()}")
        
        connection_socket.sendall(request_str.encode())
        
        # Read chunk header and data
        t_start = time.time()
        header = connection_socket.recv(4)
        
        if not header or len(header) < 4:
            print(f"Error: Received invalid header: {header}")
            safe_close_socket()
            return None, None
            
        chunk_size = int.from_bytes(header, byteorder='big')
        print(f"Chunk size from header: {chunk_size}")
        
        if chunk_size == 0:
            print("Error: Chunk size is zero")
            safe_close_socket()
            return None, None
            
        datachunk = bytearray()
        received = 0
        
        while received < chunk_size:
            data = connection_socket.recv(min(4096, chunk_size - received))
            if not data:
                print(f"Connection closed after receiving {received} of {chunk_size} bytes")
                break
            datachunk.extend(data)
            received += len(data)
            
        t_finish = time.time()
        
        if received < chunk_size:
            print(f"Warning: Incomplete chunk - received {received} of {chunk_size} bytes")
            safe_close_socket()
            return None, None
            
        return datachunk, (t_finish - t_start)
    except Exception as e:
        print(f"Error getting chunk: {e}")
        safe_close_socket()
        return None, None

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    global connection_socket
    
    print("Starting client()")
    manifest_response, _ = get_manifest_and_chunks(server_addr, server_port, video_name)
    
    if manifest_response is None or manifest_response.lower() == "video not found":
        print("video not found")
        with open("log.txt", "w") as log_file:
            log_file.write(f"{video_name} not found\n")
        return

    print("Raw manifest response received:")
    print(repr(manifest_response))
    raw_manifest = manifest_response
    respondingToManifest = raw_manifest.strip()
    print("Manifest string after stripping:")
    print(repr(respondingToManifest))
    
    if respondingToManifest.lower() == "video not found":
        print("video not found")
        with open("log.txt", "w") as log_file:
            log_file.write(f"{video_name} not found\n")
        return

    try:
        root = ET.fromstring(respondingToManifest)
        representations = root.findall(".//Representation")
        bitratesAvailable = [int(rep.attrib['bandwidth']) for rep in representations]
        durationMPD = float(root.attrib.get("mediaPresentationDuration", "30.0"))
        maxSegmentDuration = float(root.attrib.get("maxSegmentDuration", "1.0"))
        totalChunk = int(durationMPD / maxSegmentDuration)
    except Exception as e:
        print(f"Error parsing manifest: {e}")
        print("video not found")
        with open("log.txt", "w") as log_file:
            log_file.write(f"Error parsing manifest: {respondingToManifest}\n")
        return

    print(f"Parsed Manifest: Available bitrates: {bitratesAvailable}")
    print(f"Total Chunks: {totalChunk}")

    throughput = None
    indexChunk = 0
    connectionstart = time.time()
    
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    
    print("Opening log.txt for writing")
    open("log.txt", "w").close()
        
    while indexChunk < totalChunk:
        print(f"Requesting chunk {indexChunk}")
        if throughput is None or throughput <= 0:
            bitrateChoice = min(bitratesAvailable)
        else:
            valid = [b for b in bitratesAvailable if throughput >= 1.5 * b]
            bitrateChoice = max(valid) if valid else min(bitratesAvailable)
        
        datachunk, downloadTime = get_manifest_and_chunks(server_addr, server_port, video_name, 
                                                        bitrateChoice, indexChunk)
        
        if datachunk is None or downloadTime is None:
            print(f"Failed to get chunk {indexChunk}, trying again with minimum bitrate")
            if bitrateChoice != min(bitratesAvailable):
                bitrateChoice = min(bitratesAvailable)
                datachunk, downloadTime = get_manifest_and_chunks(server_addr, server_port, video_name, 
                                                                bitrateChoice, indexChunk)
                
            if datachunk is None or downloadTime is None:
                print(f"Failed to get chunk {indexChunk} even with lowest bitrate, exiting")
                safe_close_socket()
                break

        print(f"Chunk size: {len(datachunk)} bytes")
        print(f"Chunk {indexChunk} download time: {downloadTime:.3f} seconds")

        if downloadTime > 0:
            T_new = (len(datachunk) * 8) / downloadTime
        else:
            T_new = 0
        if throughput is None:
            throughput = T_new
        else:
            throughput = alpha * T_new + (1 - alpha) * throughput

        print(f"Chunk {indexChunk} throughput: current = {T_new:.2f} bps, EWMA = {throughput:.2f} bps")

        chunk_filename = f"tmp/{video_name}-{bitrateChoice}-{indexChunk:05d}.m4s"
        try:
            with open(chunk_filename, "wb") as f:
                f.write(datachunk)
        except Exception as e:
            print(f"Error saving chunk: {e}")
            continue
        
        timesinceconnection = time.time() - connectionstart
        # Log with 6 decimal places for download time
        log_line = (f"{timesinceconnection:.3f} {downloadTime:.6f} {T_new:.2f} "
                    f"{throughput:.2f} {bitrateChoice} {os.path.basename(chunk_filename)}\n")
        
        print(f"Writing to log.txt: {log_line.strip()}")
        try:
            with open("log.txt", "a") as log_file:
                log_file.write(log_line)
                log_file.flush()  
            print("Successfully logged to log.txt")
        except Exception as e:
            print(f"Error writing to log file: {e}")
        
        chunks_queue.put(chunk_filename)
        indexChunk += 1

    safe_close_socket()
    print("Process finished, Client exiting...")

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python3 client.py <network_addr> <network_port> <name> <alpha>")
        sys.exit(1)
    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    video_name = sys.argv[3]
    alpha = float(sys.argv[4])
    chunks_queue = Queue()
    client_thread = threading.Thread(target=client, args=(server_addr, server_port, video_name, alpha, chunks_queue))
    client_thread.start()
    #play_chunks(chunks_queue)