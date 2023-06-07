import libTinyFS, libDisk, datetime, sys

def main():
    disk = libTinyFS.tfs_mkfs("test", 10240)
    libDisk.writeBlock(disk, 1, libTinyFS.InodePairToBinaryArray("foo.txt", 10))
    print(libTinyFS.getInodePairBlockNum(disk, "foo.txt"))

    

if __name__ == "__main__":
    main()