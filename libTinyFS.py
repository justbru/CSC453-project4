import libDisk, sys, errorCodes, datetime


# The default size of the disk and file system block
BLOCKSIZE = 256

# Your program should use a 10240 byte disk size giving you 40 blocks total. 
# This is the default size. You must be able to support different possible values, or report 
# an error if it exceeds the limits of your implementation.
DEFAULT_DISK_SIZE = 10240

# use this name for a default disk file name 
#define DEFAULT_DISK_NAME “tinyFSDisk” 	
DEFAULT_DISK_NAME = "tinyFSDisk"

class FileEntry():
    def __init__(self, name, fp):
        self.name = name
        self.fp = fp

openFiles = []

currDisk = None

def InodePairToBinaryArray(name, number):
    inodePairByteArray = bytearray(9)
    if (len(name) > 8):
        exit(1) # Add new error message

    name = bytes(name, encoding="utf8")
    
    for x in range(0, 8):
        if x >= len(name):
            inodePairByteArray[x] = 0x00
        else:
            inodePairByteArray[x] = name[x]

    inodePairByteArray[8] = number

    return bytes(inodePairByteArray)


def writeInodePair(binaryInodePair):
    pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location] == 0:
            break
        location += 9

    for x in range(0, 8):
        pairs[x + location] = binaryInodePair[x]
    
    libDisk.writeBlock(currDisk, 1, pairs)

    return 0
 
    
def getInodePairBlockNum(filename):
    success, pairs = libDisk.readBlock(currDisk, 1)
    location = 0
    while (location < BLOCKSIZE):
        if pairs[location:location+8] == InodePairToBinaryArray(filename, 0)[0:8]:
            return pairs[location + 8]
        else:
            location += 9
    return 0


def inodeToBinaryArray(size, timestamp):
    # size times array
    inode = bytearray(256)
    inode[0] = (size / 256) + 1 # may need to change later, but one byte cannot store more than 256 int value and the size parameter passed in is represented as bytes
    timestamp = bytes(timestamp, encoding="utf8")
    
    for x in range(0, 19):
        if x >= len(timestamp):
            inode[x] = 0x00
        else:
            inode[x] = timestamp[x]

    return bytes(inode)


def readInode(blockContent):
    size = blockContent[0]
    timestamp = blockContent[1:20].decode()
    array = blockContent[20:255]
    return size, timestamp, array


def getInodeArrayEntry(inodeBlockContent, index):
    size = inodeBlockContent[0]
    array = inodeBlockContent[20:255]

    # go to array[index], make sure index is not greater than size. return value
    
    
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

    for x in range(nBytes):
        libDisk.writeBlock(disk, x, bytes("", encoding='utf8'))

    numBlocks = nBytes / BLOCKSIZE

    # Superblock setup
    superBlock = bytearray(256)
    superBlock[0] = 0x5A
    libDisk.writeBlock(disk, 0, bytes(superBlock))

    return disk

    

# tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’. 
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount 
# operation, tfs_mount should verify the file system is the correct type. Only one file 
# system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted 
# file system. Must return a specified success/error code. 
def tfs_mount(filename):
    global currDisk
    currDisk = libDisk.openDisk(filename, 0)
    status, data = libDisk.readBlock(currDisk, 0, None)

    # check if filename is initialized as an FS
    if data[0] != 0x5A:
        errorCodes.error_exit(-24);
    
    data[1] = 0x01
    status = libDisk.writeBlock(currDisk, 0, data)

    return status


def tfs_unmount():
    global currDisk
    status, data = libDisk.readBlock(currDisk, 0, None)
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
    global openFiles
    fd = len(openFiles) # new file descriptor is the index of the appended file
    openFile = FileEntry(name, fd) # create new fileEntry
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
    superBlock = libDisk.readBlock(currDisk, 0)
    inodeBlock = 0
    freeBlock = 0
    
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
    
    arrIndex = 20
    # iteratively write data blocks from buffer while storing disk block indexes in inode array
    for x in range(0, (int)(size / 256) + 1):
        # -> check the free bytemap for where to put next new piece of data
        for x in range(2, 256):
            if (superBlock[x] == 0):
                freeBlock = x # set next free block
                newInode[arrIndex] = freeBlock # assign current array index to the next free block
                arrIndex += 1 # increment index in inode direct indexing array
                superBlock[x] = 1 # update blockMap
                break
        if (x == (int)(size / 256)):
            libDisk.writeBlock(currDisk, freeBlock, buffer[256*x:]) # write only remaining bytes, avoids error
        else:
            libDisk.writeBlock(currDisk, freeBlock, buffer[256*x: 256*(x+1)]) # write all 256 bytes
            
    libDisk.writeBlock(currDisk, inodeBlock, newInode)
    libDisk.writeBlock(currDisk, 0, superBlock)

    return 0 # return int


# deletes a file and marks its blocks as free on disk.
def tfs_delete(fd):
    global openFiles
    global currDisk
    fileName = openFiles[fd].name # get filename of file to be deleted by looking up in dynamic table
    openFiles[fd] = None # set to None, not pop; this preserves the file descriptor of other open files

    superBlock = libDisk.readBlock(currDisk, 0) # read superblock
    inodeLoc = getInodePairBlockNum(fileName) # get inode location of file to be deleted
    inode = libDisk.readBlock(currDisk, inodeLoc) # get inode data of file to be deleted

    superBlock[inodeLoc] = 0 # set inode location in free bock map to 0
    
    # Cycle through the values in the direct index array of the inode and update free block map
    for x in range(20, 256):
        if (inode[x] == 0):
            break
        else:
            superBlock[inode[x]] = 0 # set the block location in the free block map to 0
            break

    libDisk.writeBlock(currDisk, 0, superBlock) # update superblock with new update free block map

    return 0 # return int


# reads one byte from the file and copies it to ‘buffer’, using the current file 
# pointer location and incrementing it by one upon success. If the file pointer is already 
# at the end of the file then tfs_readByte() should return an error and not increment 
# the file pointer.
def tfs_readByte(fd):
    global openFiles
    global currDisk

    filename = openFiles[fd].name
    inodeLoc = getInodePairBlockNum(filename)
    inode = libDisk.readBlock(currDisk, inodeLoc)

    if (openFiles[fd].fp > inode[0] * 256):
        return -1, 0 # change later with a new custom error code

    inodeBlockOffset = openFiles[fd].fp / 256 # get the block offset within the inode direct index array
    blockData = libDisk.readBlock(currDisk, inode[20 + inodeBlockOffset]) # retrieve the block that contains the desired byte
    desiredByte = blockData[openFiles[fd].fp % 256] # retrieve the desired byte
    openFiles[fd].fp += 1 # increment fp of file

    return 0, desiredByte # return int

# change the file pointer location to offset (absolute). Returns success/error codes.
def tfs_seek(fd, offset):
    global openFiles
    openFiles[fd].fp += offset # increment fp by offset
    return 0 # return int
