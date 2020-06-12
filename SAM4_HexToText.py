import sys

# = /* CRC lookup table [B]polynomial 0xA001[/B] */
crc16tab =  [
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
]

MEMORY_ARRAY_SIZE = 0x100000
BASE_ADDRESS = 0x1000000
SAM4C_PAGE_SIZE = 512
ETX = 0x3

def get_crc(data_array,starting_point,number_of_bytes,starting_value):
    ret_val = starting_value
    #print("Starting value is " + hex(starting_point) + " number of bytes is " + hex(number_of_bytes))
    for i in range(starting_point, starting_point + number_of_bytes):
        latestValue = (data_array[i] & 0xFF)
        index = ((ret_val ^ latestValue) & 0xff);
        ret_val = crc16tab[index] ^ ((ret_val >> 8) & 0xFF)
    return ret_val
        
def get_crc_from_string(istr,start_value):
    ret_val = start_value
    slen = len(istr)
    #print("The incoming string is " + istr)
    for i in range(0,slen):    
        value = ord(istr[i])
        #print("value is " + hex(value))
        if value != 0x20 and value != 0x0A and value != 0x0D:
            aval = value   
            index = ((ret_val ^ (aval & 0xFF)) & 0xff)
            ret_val = (crc16tab[index] ^ ((ret_val >> 8) & 0xFF))
            #print("Index is " + hex(index) + " crc lookup is " + hex(crc16tab[index]))
    return ret_val
        
        
    
    

def create_page(address,nfw,marr):
    line_index = 0
    line_string = ""
    page_string = ""
    #print("Writing a page at address ", hex(BASE_ADDRESS + address))
    page_string = "* " + format(BASE_ADDRESS + address,'x').zfill(7) + " " + format(SAM4C_PAGE_SIZE,'x').zfill(3) + "\r\n"   
    
    for a in range(0,SAM4C_PAGE_SIZE):
        line_index += 1
        new_value = (marr[address + a] & 0xFF)
        new_string = format(new_value,'x').zfill(2)
        line_string += new_string
        if line_index == 16:
            #nfw.write(line_string + "\r\n")
            page_string += line_string + "\r\n"
            line_index = 0
            line_string = ""
        else:
            line_string += " "
    if line_index != 0:
        page_string += line_string
    
    crc = get_crc_from_string(page_string,0xFFFF)
    #print("The CRC is " + hex(crc))
    #nfw.write(format((crc >> 8) & 0xFF,'x').zfill(2) + " " + format(crc  & 0xFF,'x').zfill(2) + " " + chr(ETX) + "\r\n")
    page_string += format((crc >> 8) & 0xFF,'x').zfill(2) + " " + format(crc  & 0xFF,'x').zfill(2) + " " + chr(ETX) + "\r\n"
     
     
    nfw.write(page_string)
    
    
    
    
def check_page_bondary(address,marr):
    #print("Check page boundary starting at " + hex(address))
    if address % SAM4C_PAGE_SIZE == 0:
        ret_val = True
    else:
        ret_val = False
        
    if ret_val:
        dataInPage = False;
        #print("Check from address " + hex(address) + " to " + hex(address + SAM4C_PAGE_SIZE))
        for a in range(address, address + SAM4C_PAGE_SIZE):
            if marr[a] != 0xFFFF:
                dataInPage = True                
        if not dataInPage:
            ret_val = False
                        
    return ret_val


###########################################################
def write_new_file(new_file,memory_array,end_address):
    first_page = True
    highest_address = 0
    create_erase_section(new_file,0,memory_array)
    for addr in range(0, MEMORY_ARRAY_SIZE):
        if check_page_bondary(addr,memory_array):
            if first_page:                
                lowest_address = addr                
                first_page = False
            else:
                highest_address = addr            
            new_line = create_page(addr,new_file,memory_array)
    highest_address += SAM4C_PAGE_SIZE    
    crc = get_crc(memory_array,lowest_address,highest_address-lowest_address,0xFFFF)
    crc_string = "# " +  format(lowest_address + BASE_ADDRESS,'x').zfill(7) + " " + format(+ BASE_ADDRESS + highest_address,'x').zfill(7)   
    crc_string += " " + format((crc >> 8) & 0xFF,'x').zfill(2) + " " + format(crc  & 0xFF,'x').zfill(2) + " " + chr(ETX)
    new_file.write(crc_string)
    new_file.close()
###########################################################

###########################################################
def detect_data_in_page(start_addr,mem_arr):
    ret_val = False;
    for a in (start_addr,start_addr + SAM4C_PAGE_SIZE):
        if mem_arr[a] != 0xFF:
            ret_val = True;
            a = start_addr + SAM4C_PAGE_SIZE
    return ret_val
###########################################################

###########################################################
def create_erase_section(file_ref,start_address,m_arr):
    first_line = True
   # print("Create Erase Section")
    a = start_address
    while a < MEMORY_ARRAY_SIZE:
        #print("check boundary starting at ", hex(a))
        if check_page_bondary(a,m_arr):
            if detect_data_in_page(a,m_arr):
                if first_line:
                    lowest_address = BASE_ADDRESS + a
                    first_line = False
                else:                
                    highest_address = BASE_ADDRESS + a
        a += SAM4C_PAGE_SIZE
    highest_address += SAM4C_PAGE_SIZE
                
    file_ref.write("$ " + format(lowest_address,'x').zfill(7) + " " + format(highest_address,'x').zfill(7) + "\r\n")
        
    
###########################################################    

# Start of program

memory_array = []
for y in range(0, MEMORY_ARRAY_SIZE):
    memory_array.append(0xFFFF)
    
f = open(sys.argv[1])
line_array = []
offset = BASE_ADDRESS
for l in range(0,16):
    line_array.append(0xFFFF)
# use readline() to read the first line 
line = f.readline()
# use the read line to read further.
# If the file is not empty keep reading one line
# at a time, till the file is empty
while line:
# in python 3 print is a builtin function, so
    for l in range(0,16):
        line_array[l] = 0xFFFF;
    if line[0] == ':':        
        tempStr = line[1:3]                   # Next is the number of data bytes
        bytes_in_line = int(tempStr, base=16)
        tempStr = line[7:9];                   
        data_type = int(tempStr, base=16) 
        if data_type == 0:
            tempStr = line[3:7]
            address = int(tempStr, base=16) 
            #print("Address is ", hex(address))
            data_string = ""
            for l in range(0,bytes_in_line):
                tempStr = line[(9+(l*2)):(9+(l*2)) + 2] 
                line_array[l] = int(tempStr, base=16) 
            tempStr = line[(9+(bytes_in_line*2)):(9+(bytes_in_line*2)) + 2]
            crc = int(tempStr, base=16)
            #print("CRC is ", hex(crc))   
            for l in range(0,bytes_in_line):                
                if line_array[l] < 0xFFFF:
                    addressToProgram = (offset-BASE_ADDRESS);
                    addressToProgram += (address + l)
                    memory_array[addressToProgram] = line_array[l]
        elif data_type == 4:
            tempStr = line[9:13]               # Get the offset address
            offset = ((int(tempStr, base=16) << 16) & 0xFFFF0000)
            print("Offset address is ", hex(offset))
                #data_string += tempStr + " "
            #print (data_string)
        elif data_type == 1:
            end_address = offset + address + l + 1
            print("End address is ", hex(end_address))        
    line = f.readline()    
f.close()
new_filename = sys.argv[1] + ".txt"
fw= open(new_filename,"w+")
write_new_file(fw,memory_array,end_address)
