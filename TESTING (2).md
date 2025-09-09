# CSEE 4119 Spring 2025, Assignment 1 Testing File
## Your name Roni Herschmann
## GitHub username: ron21112
# Final Version

Test Case Breakdown:

Case 1: High Bandwidth
Bandwidth File: test1_high.txt
Content: 0:3000000
Alpha Value: 0.5
Expected Behavior:
Highest available bitrate selection
Stable throughput estimation

Case 2: Low Bandwidth Scenario
Bandwidth File: test2_low.txt
Content: 0:400000
Alpha Value: 0.5
Expected Behavior:
Lowest bitrate selection (292312 bps)
Minimal video quality to ensure streaming

Case 3: Dynamic Bandwidth Scenario
Bandwidth File: test3_step.txt
Content:
 0:4000008:200000016:400000


Configuration:
Initial low bandwidth (400 Kbps)
Mid-test bandwidth increase to 2 Mbps
Return to low bandwidth
Alpha Value: 0.5
Expected Behavior:
Dynamic bitrate adaptation
Bitrate changes reflecting bandwidth shifts

Low Alpha Value
Bandwidth File: test4_alpha.txt
Content:
 0:5000005:2000000


Configuration:
Initial bandwidth of 500 Kbps
Bandwidth increase to 2 Mbps
Alpha Value: 0.1 (conservative smoothing)
Expected Behavior:
Slower throughput estimation updates
More stable but less responsive bitrate selection


Log File Format
<time> <duration> <tput> <avg-tput> <bitrate> <chunkname>


Sample Log Entry Breakdown
0.357 0.36 353084.17 353084.17 292312 chunk_0.m4s


Time Since Connection: 0.357 seconds
Chunk Download Duration: 0.36 seconds
Current Throughput: 353,084.17 bps
Average Throughput: 353,084.17 bps
Selected Bitrate: 292,312 bps
Chunk Filename: chunk_0.m4s

Sample log.txt file after running the programs:
rlh2177@instance-20250225-233747:~$ cat log.txt
0.288 0.287096 437903.00 437903.00 292312 bunny-292312-00000.m4s
0.723 0.434170 336863.62 387383.31 292312 bunny-292312-00001.m4s
1.274 0.550124 358493.77 372938.54 292312 bunny-292312-00002.m4s
1.661 0.386192 438227.25 405582.89 292312 bunny-292312-00003.m4s
2.142 0.479776 346695.02 376138.96 292312 bunny-292312-00004.m4s
2.421 0.277979 583726.76 479932.86 292312 bunny-292312-00005.m4s
2.700 0.278850 584973.84 532453.35 292312 bunny-292312-00006.m4s
2.986 0.284570 591600.91 562027.13 292312 bunny-292312-00007.m4s
3.169 0.181906 914452.79 738239.96 292312 bunny-292312-00008.m4s
3.346 0.175867 914554.33 826397.15 292312 bunny-292312-00009.m4s
3.517 0.170570 914579.80 870488.47 292312 bunny-292312-00010.m4s
3.808 0.289753 916144.44 893316.46 292312 bunny-292312-00011.m4s
4.032 0.223825 914534.05 903925.25 292312 bunny-292312-00012.m4s
4.134 0.101146 2001770.51 1452847.88 292312 bunny-292312-00013.m4s
4.238 0.102583 4619637.92 3036242.90 612790 bunny-612790-00014.m4s
4.510 0.271162 5897851.51 4467047.20 1791962 bunny-1791962-00015.m4s
4.655 0.144180 5929539.89 5198293.55 1791962 bunny-1791962-00016.m4s
4.932 0.274800 3766203.29 4482248.42 1791962 bunny-1791962-00017.m4s
5.049 0.115673 5918152.35 5200200.38 1791962 bunny-1791962-00018.m4s
5.269 0.219016 5951825.31 5576012.85 1791962 bunny-1791962-00019.m4s
5.617 0.346411 5909396.82 5742704.83 3676374 bunny-3676374-00020.m4s
5.919 0.301270 3931094.72 4836899.77 3676374 bunny-3676374-00021.m4s
7.349 1.428364 1595895.95 3216397.86 1791962 bunny-1791962-00022.m4s
8.565 1.215349 1463961.43 2340179.65 1791962 bunny-1791962-00023.m4s
9.033 0.466599 1588362.59 1964271.12 987680 bunny-987680-00024.m4s
9.498 0.464093 1593644.57 1778957.84 987680 bunny-987680-00025.m4s
9.966 0.466304 1593346.61 1686152.23 987680 bunny-987680-00026.m4s
11.661 1.693340 439226.54 1062689.38 987680 bunny-987680-00027.m4s
12.537 0.875239 439011.33 750850.36 612790 bunny-612790-00028.m4s
12.909 0.371690 438473.44 594661.90 292312 bunny-292312-00029.m4s

Conclusion:
Test cases demonstrate the adaptive bitrate streaming clients ability to respond to different network conditions. 
