import libDisk, sys, errorCodes, datetime

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"


class FileEntry():
    def __init__(self, name, fp):
        self.name = name
        self.fp = fp

openFiles = []
fileSystems = dict()
currDisk = None

def InodePairToBinaryArray(name, number):
    inodePairByteArray = bytearray(9)
    if (len(name) > 8):
        errorCodes.error_exit(-23);

    name = bytes(name, encoding="utf8")
    for x in range(0, 8):
        if x >= len(name):
            inodePairByteArray[x] = 0x00
        else:
            inodePairByteArray[x] = name[x]

    inodePairByteArray[8] = number
    return bytes(inodePairByteArray)


def writeInodePair(binaryInodePair):
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0

    while (location < BLOCKSIZE):
        if pairs[location] == 0:
            break
        location += 9

    for x in range(0, 9):
        pairs[x + location] = binaryInodePair[x]
    
    libDisk.writeBlock(currDisk, 1, pairs)
    return 0

def deleteInodePair(filename):
    global currDisk
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location:location+8] == InodePairToBinaryArray(filename, 0)[0:8]:
            break
        else:
            location += 9

    for x in range(location, location + 9):
        pairs[x] = 0x00

    return pairs
        

 
    
def getInodePairBlockNum(filename):
    global currDisk
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location:location+8] == InodePairToBinaryArray(filename, 0)[0:8]:
            return pairs[location + 8]
        else:
            location += 9
    return -1


def inodeToBinaryArray(size, timestamp):
    inode = bytearray(256)
    inode[0] = (int) (size / 256) + 1 # may need to change later, but one byte cannot store more than 256 int value and the size parameter passed in is represented as bytes
    timestamp = bytes(timestamp, encoding="utf8")

    return bytearray(inode)


def updateCreationTimestamp(inodeContent):
    timestamp = bytes(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), encoding="utf8")
    
    for x in range(1, 20):
        if x > len(timestamp) + 1:
            inodeContent[x] = 0x00
        else:
            inodeContent[x] = timestamp[(x - 1) % 19]
    return inodeContent


def updateModifiedTimestamp(inodeContent):
    timestamp = bytes(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), encoding="utf8")
    
    for x in range(20, 39):
        if x > len(timestamp) + 20:
            inodeContent[x] = 0x00
        else:
            inodeContent[x] = timestamp[(x - 1) % 19]
    return inodeContent


def updateAccessTimestamp(inodeContent):
    timestamp = bytes(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), encoding="utf8")
    
    for x in range(39, 58):
        if x > len(timestamp) + 39:
            inodeContent[x] = 0x00
        else:
            inodeContent[x] = timestamp[(x - 1) % 19]
    return inodeContent

    
# returns the file’s creation time or all info (up to you if you want to make multiple functions) */
def tfs_stat(fd):
    if currDisk is None:
        errorCodes.error_exit(-25)

    filename = openFiles[fd].name
    inodeLoc = getInodePairBlockNum(filename)
    success, inode = libDisk.readBlock(currDisk, inodeLoc)

    print("Creation time: ", end='')
    for x in range (1, 20):
        print(chr(inode[x]), end='')
    print()

    print("Modificaiton time: ", end='')
    for x in range (20, 39):
        print(chr(inode[x]), end='')
    print()

    print("Access time: ", end='')
    for x in range (39, 58):
        print(chr(inode[x]), end='')
    print()

    return 0;


# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’. 
# This function should use the emulated disk library to open the specified file, and
#  upon success, format the file to be mountable. This includes initializing all data 
# to 0x00, setting magic numbers, initializing and writing the superblock and other 
# metadata, etc. Must return a specified success/error code. 
def tfs_mkfs(filename, nBytes):
    if filename is None:
        disk = libDisk.openDisk(DEFAULT_DISK_NAME, nBytes)
    else:
        disk = libDisk.openDisk(filename, nBytes)

    for i in range((int)(nBytes/256)):
        libDisk.writeBlock(disk, i, bytearray(256))
    
    # Superblock setup
    superBlock = bytearray(256)
    superBlock[0] = 0x5A
    libDisk.writeBlock(disk, 0, bytes(superBlock))

    global fileSystems
    fileSystems[filename] = disk

    return disk

    

# tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’. 
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount 
# operation, tfs_mount should verify the file system is the correct type. Only one file 
# system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted 
# file system. Must return a specified success/error code. 
def tfs_mount(filename):
    global currDisk
    global fileSystems
    currDisk = fileSystems[filename]
    status, superblock = libDisk.readBlock(currDisk, 0)

    # check if filename is initialized as an FS
    if superblock[0] != 0x5A:
        errorCodes.error_exit(-24);
    
    superblock[1] = 0x01
    status = libDisk.writeBlock(currDisk, 0, superblock)

    return status

def tfs_unmount():
    global currDisk
    status, data = libDisk.readBlock(currDisk, 0)
    data[1] = 0x00
    status = libDisk.writeBlock(currDisk, 0, data)

    global openFiles
    openFiles.clear()

    return status

# Opens a file for reading and writing on the currently mounted file system. Creates a 
# dynamic resource table entry for the file (the structure that tracks open files, the 
# internal file pointer, etc.), and returns a file descriptor (integer) that can be used 
# to reference this file while the filesystem is mounted. 
def tfs_open(name):
    if (len(name) > 8):
        errorCodes.error_exit(-23)
        return -23
    
    global openFiles
    fd = len(openFiles) # new file descriptor is the index of the appended file
    openFile = FileEntry(name, 0) # create new fileEntry
    openFiles.append(openFile) # append to the list of open files
    return fd; # returns a fileDescriptor


# Closes the file and removes dynamic resource table entry
def tfs_close(fd):
    global openFiles
    openFiles[fd] = None # set to None, not pop; this preserves file descriptors 
    return 0 # return int


# Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, 
# to the file described by ‘FD’. Sets the file pointer to 0 (the start of file) when 
# done. Returns success/error codes.
def tfs_write(fd, buffer, size):
    global currDisk
    global openFiles
    success, superBlock = libDisk.readBlock(currDisk, 0)
    inodeBlock = 0
    freeBlock = 0
    newInode = None

    # file is not open
    if openFiles[fd] is None:
        errorCodes.error_exit(-27)
        
    # file does not exist
    if getInodePairBlockNum(openFiles[fd].name) == -1:
       
        # Find next free block in blockMap in superblock
        for x in range(2, 256):
            if (superBlock[x] == 0):
                inodeBlock = x
                superBlock[x] = 1
                break

        # add <openFiles[fd].filename, next free block> to the root inode on disk (index 1)
        writeInodePair(InodePairToBinaryArray(openFiles[fd].name, inodeBlock))
        
        # make a new inode at the next free block ^ with size, timestamp, and array with size 'size'
        newInode = inodeToBinaryArray(size, datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                
        # update modification time
        newInode = updateCreationTimestamp(newInode)
        newInode = updateModifiedTimestamp(newInode)
        newInode = updateAccessTimestamp(newInode)
    
    # File does already exist
    else:
        inodeBlock = getInodePairBlockNum(openFiles[fd].name)
        success, currInode = libDisk.readBlock(currDisk, inodeBlock)
       
        for i in range(59, 59 + currInode[0]):
            superBlock[currInode[i]] = 0
            
        newInode = inodeToBinaryArray(size, datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    
        newInode[1:20] = currInode[1:20]
        newInode = updateModifiedTimestamp(newInode)
        newInode = updateAccessTimestamp(newInode)

        openFiles[fd].fp = 0        

    arrIndex = 59
        # iteratively write data blocks from buffer while storing disk block indexes in inode array
    for x in range(0, (int)(size / 256) + 1):
        # -> check the free bytemap for where to put next new piece of data
        for i in range(2, 256):
            if (superBlock[i] == 0):
                freeBlock = i # set next free block
                newInode[arrIndex] = freeBlock # assign current array index to the next free block
                arrIndex += 1 # increment index in inode direct indexing array
                superBlock[i] = 1 # update blockMap
                break
        if (x == (int)(size / 256)):
            libDisk.writeBlock(currDisk, freeBlock, buffer[256*x:]) # write only remaining bytes, avoids error
        else:
            libDisk.writeBlock(currDisk, freeBlock, buffer[256*x: 256*(x+1)]) # write all 256 bytes

    libDisk.writeBlock(currDisk, inodeBlock, newInode)
   # libDisk.writeBlock(currDisk, inodeBlock, newInode)
    libDisk.writeBlock(currDisk, 0, superBlock)

    return 0 # return int

# deletes a file and marks its blocks as free on disk.
def tfs_delete(fd):
    global openFiles
    global currDisk
    fileName = openFiles[fd].name # get filename of file to be deleted by looking up in dynamic table
    openFiles[fd] = None # set to None, not pop; this preserves the file descriptor of other open files

    success, superBlock = libDisk.readBlock(currDisk, 0) # read superblock
    inodeLoc = getInodePairBlockNum(fileName) # get inode location of file to be deleted
    success, inode = libDisk.readBlock(currDisk, inodeLoc) # get inode data of file to be deleted

    superBlock[inodeLoc] = 0 # set inode location in free bock map to 0
    
    # Cycle through the values in the direct index array of the inode and update free block map
    for x in range(20, 256):
        if (inode[x] == 0):
            break
        else:
            superBlock[inode[x]] = 0 # set the block location in the free block map to 0
            break

    currNode = deleteInodePair(fileName)
    libDisk.writeBlock(currDisk, 1, currNode)
    libDisk.writeBlock(currDisk, 0, superBlock) # update superblock with new update free block map

    return 0 # return int


# reads one byte from the file and copies it to ‘buffer’, using the current file 
# pointer location and incrementing it by one upon success. If the file pointer is already 
# at the end of the file then tfs_readByte() should return an error and not increment 
# the file pointer.
def tfs_readByte(fd):
    global openFiles
    global currDisk

    if currDisk is None:
        errorCodes.error_exit(-25)

    filename = openFiles[fd].name
    inodeLoc = getInodePairBlockNum(filename)
    success, inode = libDisk.readBlock(currDisk, inodeLoc)

    if (openFiles[fd].fp > inode[0] * 256): # file pointer at end
        errorCodes.error_exit(-26)
        return -26, None

    inodeBlockOffset = (int) (openFiles[fd].fp / 256) # get the block offset within the inode direct index array
    success, blockData = libDisk.readBlock(currDisk, inode[59 + inodeBlockOffset]) # retrieve the block that contains the desired byte
    desiredByte = blockData[openFiles[fd].fp % 256] # retrieve the desired byte
    openFiles[fd].fp += 1 # increment fp of file

    # update access time
    newInode = updateAccessTimestamp(inode) # add function call riley is making
    libDisk.writeBlock(currDisk, inodeLoc, newInode)

    return 0, desiredByte # return int


# change the file pointer location to offset (absolute). Returns success/error codes.
def tfs_seek(fd, offset):
    global openFiles
    openFiles[fd].fp += offset # increment fp by offset
    return 0 # return int


# Renames a file.  New name should be passed in. 
def tfs_rename(oldName, newName):
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location:location+8] == InodePairToBinaryArray(oldName, 0)[0:8]:
            newName = bytes(newName, encoding="utf8")
            for x in range(location, location + 8):
                if x >= len(newName):
                    pairs[x] = 0x00
                else:
                    pairs[x] = newName[x]
            libDisk.writeBlock(currDisk, 1, pairs)
            return 0  
        else:
            location += 9
    return -1


# lists all the files and directories on the disk
def tfs_readdir():
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location] != 0:
            for x in range (location, location + 8):
                print(chr(pairs[x]), end='')
            print()
        location += 9
    return -1
