import libTinyFS, libDisk, datetime, sys, time

def main():
    print("creating file system under test.txt")
    disk = libTinyFS.tfs_mkfs("test.txt", 10240)

    print("mounting test.txt file system")
    libTinyFS.tfs_mount("test.txt")

    print("creating file foo.txt")
    file1 = libTinyFS.tfs_open("foo.txt")

    print("writing \"hello there\" to foo.txt")
    libTinyFS.tfs_write(file1, bytes("hello there", encoding="utf8"), 11)

    print("creating file bar.txt")
    file2 = libTinyFS.tfs_open("bar.txt")

    print("writing \"goodbye\" to bar.txt")
    libTinyFS.tfs_write(file2, bytes("goodbye", encoding="utf8"), 8)

    print("printing from file 1: ", end='')
    for x in range(0, 11):
        success, data = libTinyFS.tfs_readByte(file1)
        print(chr(data), end="")
    print()

    print("printing from file 2: ", end = '')
    for x in range(0, 8):
        success, data = libTinyFS.tfs_readByte(file2)
        print(chr(data), end="")
    print()
    
    print("rewriting foo.txt")
    print("writing \"rewrote foo.txt\" to foo.txt")
    libTinyFS.tfs_write(file1, bytes("rewrote foo.txt", encoding="utf8"), 15)

    print("printing from file 1: ", end='')
    for x in range(0, 15):
        success, data = libTinyFS.tfs_readByte(file1)
        print(chr(data), end="")
    print()

    print("foo.txt stats:")
    libTinyFS.tfs_stat(file1)

    print("closing foo.txt")
    libTinyFS.tfs_close(file1)

    print("waiting 3 seconds")
    time.sleep(3)

    print("opening file foo.txt")
    file1 = libTinyFS.tfs_open("foo.txt")

    print("printing from file 1: ", end='')
    for x in range(0, 15):
        success, data = libTinyFS.tfs_readByte(file1)
        print(chr(data), end="")
    print()

    print("foo.txt stats:")
    libTinyFS.tfs_stat(file1)

    print("closing bar.txt")
    libTinyFS.tfs_close(file2)

    print("printing all files:")
    libTinyFS.tfs_readdir()

    print("renaming foo.txt to boo.txt")
    libTinyFS.tfs_rename("foo.txt", "boo.txt")

    print("opening file boo.txt")
    file1 = libTinyFS.tfs_open("boo.txt")

    print("printing from file 1: ", end='')
    for x in range(0, 15):
        success, data = libTinyFS.tfs_readByte(file1)
        print(chr(data), end="")
    print()

    print("printing all files:")
    libTinyFS.tfs_readdir()

    print("unmounting test.txt")
    libTinyFS.tfs_unmount()

    print("Attempting to read from bar.txt in unmounted test.txt file system")
    #success, data = libTinyFS.tfs_readByte(file2)

if __name__ == "__main__":
    main()