import sys

## @package Hex to Text file
# Reads in an Intel hex file and parses it, a line at a time 
# then turns that Intel hex file into a text file suitable
# for the SAM4 to program itself by downloading this newfile
# over HTTPS.
# The program constructs a large array the holds every value of the
# SAM's flash memory. It is initalised with every value holding 0xFFFF
# This means the program knows if a page has been filled with anything
# as at least one of the page's values will be a none 0xFFFF value as 
# it will have been overwritten with a eight bit value read from the 
# Intel hex file
# NOTE: Although the memory starts from 0x1000000 in the SAM, the array 
# obviously starts at 0, so 0x1000000 is taken off the memory address
# read in the Intel hex file and added back when writing to the new file

# = /* CRC lookup table */
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

##
# @fn get_crc(data_array,starting_point,number_of_bytes,starting_value)
# @brief
# Creates a 16-bit CRC from integers
# @param[in] data_array - the array of data from which to take the data used to create the CRC
# @param[in] starting_point - the first value in the array from where to take the data to create the CRC
# @param[in] number_of_bytes - how many bytes to use to create the CRC
# @param[in] starting_value - The initial value of the CRC
def get_crc(data_array,starting_point,number_of_bytes,starting_value):
    ret_val = starting_value    
    for i in range(starting_point, starting_point + number_of_bytes):
        latestValue = (data_array[i] & 0xFF)
        index = ((ret_val ^ latestValue) & 0xff);
        ret_val = crc16tab[index] ^ ((ret_val >> 8) & 0xFF)
    return ret_val

##
# @fn get_crc_from_string(istr,start_value):
# @brief
# Creates a 16-bit CRC from a string by reading 16-bit values from the string
# one byte at a time
# @return Returns the CRC
# @param[in] istr - the input string from which to create the CTC
# @param[in] start_value - The first position in the string from which to start
# reading the data
def get_crc_from_string(istr,start_value):
    ret_val = start_value
    slen = len(istr)    
    for i in range(0,slen):    
        value = ord(istr[i])        
        if value != 0x20 and value != 0x0A and value != 0x0D:
            aval = value   
            index = ((ret_val ^ (aval & 0xFF)) & 0xff)
            ret_val = (crc16tab[index] ^ ((ret_val >> 8) & 0xFF))            
    return ret_val
        
        
    
    
##
# @fn create_page(address,nfw,marr)
# @brief
# Creates a string which is written to the target file. 
# The sting is a page of data to be written to the SAM which starts with
# a * character, then the start address of where the data is to be written
# then the number of bytes to be written, the data that is to be written. 
# Finally a CRC is calculated and written to the end of the text to be written 
# to the file. All these values are separated by spaces to make the file easy to read.
# @param[in] address - the address in flash to where the data is to be written 
# @param[in] nfw - the file to be written to
# @param[in] marr - The prefilled array of data from which to create the page
def create_page(address,nfw,marr):
    line_index = 0
    line_string = ""
    page_string = ""    
    page_string = "* " + format(BASE_ADDRESS + address,'x').zfill(7) + " " + format(SAM4C_PAGE_SIZE,'x').zfill(3) + "\r\n"   
    
    for a in range(0,SAM4C_PAGE_SIZE):
        line_index += 1
        new_value = (marr[address + a] & 0xFF)
        new_string = format(new_value,'x').zfill(2)
        line_string += new_string
        if line_index == 16:            
            page_string += line_string + "\r\n"
            line_index = 0
            line_string = ""
        else:
            line_string += " "
    if line_index != 0:
        page_string += line_string
    
    crc = get_crc_from_string(page_string,0xFFFF)   
    page_string += format((crc >> 8) & 0xFF,'x').zfill(2) + " " + format(crc  & 0xFF,'x').zfill(2) + " " + chr(ETX) + "\r\n"
          
    nfw.write(page_string)
    
    
    
##
# @fn check_page_boundary(address,marr):   
# @brief
# Check the array to ensure that there is some data to be written
# return True or False
# @param[in] address - the start address of the page of data to check for something to write
# @param[in] marr - The array of data
def check_page_boundary(address,marr):   
    if address % SAM4C_PAGE_SIZE == 0:
        ret_val = True
    else:
        ret_val = False
        
    if ret_val:
        dataInPage = False;        
        for a in range(address, address + SAM4C_PAGE_SIZE):
            if marr[a] != 0xFFFF:
                dataInPage = True                
        if not dataInPage:
            ret_val = False
                        
    return ret_val


##
# @fn write_new_file(new_file,memory_array,end_address):
# @brief
# Write a file suitable for the SAM to read and self program
# @param[in] new_file - the new file to write to
# @param[in] memory_array - The prefilled array of SAM data, taken from the Intel hex file
# @param[in] end_address - The final address within the array from which to take data
def write_new_file(new_file,memory_array,end_address):
    first_page = True
    highest_address = 0
    create_erase_section(new_file,0,memory_array)
    for addr in range(0, MEMORY_ARRAY_SIZE):
        if check_page_boundary(addr,memory_array):
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


##
# @fn detect_data_in_page(start_addr,mem_arr):
# @brief
# Check the prefilled array to ensure that there is some data to be written
# return True or False
# @param[in] start_addr - The adress from which to start checking
# @param[in] mem_arr - The prefilled array of SAM data, taken from the Intel hex file
def detect_data_in_page(start_addr,mem_arr):
    ret_val = False;
    for a in (start_addr,start_addr + SAM4C_PAGE_SIZE):
        if mem_arr[a] != 0xFF:
            ret_val = True;
            a = start_addr + SAM4C_PAGE_SIZE
    return ret_val
###########################################################



##
# @fn create_erase_section(file_ref,start_address,m_arr):
# @brief
# Creates a string which is written to the target file. 
# The in is the start address of the SAM memory and the end address
# and written to the outout file
# This string is used by the SAM to work out which pages of memory to erase
# @param[in] file_ref - the new file to write to
# @param[in] start_address - The first address in the SAM to write to
# @param[in] m_arr - the prefilled array of memory created from  the Intel hex file
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
        

##
# @fn check_line_crc(line)
# @brief
# Checks a line of the Intel hex file to make sre its CRC is correct
# @return True iof CRC matches, false if not
# @param[in] line - a line of data read from the Intel hex file
def check_line_crc(line):
    slen = len(line)
    index = 1
    calculated_crc = 0    
    while index < (slen - 4):
        temp_str = line[index:index + 2]
        lv = int(temp_str, base=16)
        calculated_crc += lv
        calculated_crc &= 0xFF
        index += 2        
    temp_str = line[index:index + 2]
    read_crc = int(temp_str, base=16)
    calculated_crc = ~calculated_crc & 0xFF
    calculated_crc += 1
    calculated_crc &= 0xFF
        
    if calculated_crc == read_crc:
        ret_val = True
    else:
        ret_val = False
        print("Calculated CRC = " + hex(calculated_crc) + " Read CRC " + hex(read_crc))

    return ret_val

                                   
##
# @fn "Main" function of file
# @brief
# Reads in the file specified by sys.argv[1] and reads it, 
# a line at a time.
n = len(sys.argv)
if n != 3:
    if n == 2:
        if sys.argv[1] != "-h" and sys.argv[1] != "-help":
            print("Invalid arguments. Input -h or ==help for help");
    print("Input the name of the file created by WICED")
    print("and the version number of the firmware in format x.y.z")
    print("eg. snap40_shield-BCM920736TAG_Q32-rom-ram-Wiced-release.ota.bin 1.2.66")  
    sys.exit()

memory_array = []
for y in range(0, MEMORY_ARRAY_SIZE): # Prefill an  array the size of the SAM's memory 
    memory_array.append(0xFFFF)       # With 0xFFFF. When file is read it will put values of
                                      # length 8 bits into the array
    
f = open(sys.argv[1])
line_array = []
offset = BASE_ADDRESS
for l in range(0,16):
    line_array.append(0xFFFF)
# readline() gets the first line
line = f.readline()
# There is another readline at the end of this while statement 
# Keep going until there are no more lines to read
while line: 
    for l in range(0,16):   
        line_array[l] = 0xFFFF;
    if line[0] == ':':        
        tempStr = line[1:3]                     # Next is the number of data bytes in the line
        bytes_in_line = int(tempStr, base=16)
        tempStr = line[7:9];                    # Then the datatype 
        data_type = int(tempStr, base=16)       # Each line in an Intel hex file is a specific type
        if data_type == 0:                      # Type 0 is data
            tempStr = line[3:7]                 # This is the address within the page
            address = int(tempStr, base=16)             
            data_string = ""
            for l in range(0,bytes_in_line):    # Read in bytes as ASCII and turn into binary
                tempStr = line[(9+(l*2)):(9+(l*2)) + 2] 
                line_array[l] = int(tempStr, base=16) # Store into an array of the whole memory area
            tempStr = line[(9+(bytes_in_line*2)):(9+(bytes_in_line*2)) + 2]
            crc = int(tempStr, base=16)         # The last byte is the CRC of the data in the line            
            for l in range(0,bytes_in_line):    # Now store the read data in the large array of SAM's whole memory
                if line_array[l] < 0xFFFF:
                    addressToProgram = (offset-BASE_ADDRESS);
                    addressToProgram += (address + l)
                    memory_array[addressToProgram] = line_array[l]
        elif data_type == 4:                    # Te offset address (ie upper 16 butes of the address to program)
            tempStr = line[9:13]               
            offset = ((int(tempStr, base=16) << 16) & 0xFFFF0000)
            print("Offset address is ", hex(offset))
        elif data_type == 1:                    # End of file, last address
            end_address = offset + address + l + 1
            print("End address is ", hex(end_address))        
    if not check_line_crc(line):                # Ensure the 
        f.close()
        print("Invalid crc read from file")
        sys.exit()
    line = f.readline()    
f.close()
new_filename = sys.argv[1] + ".txt"
fw= open(new_filename,"w+")
write_new_file(fw,memory_array,end_address)
