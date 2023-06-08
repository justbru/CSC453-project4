import libTinyFS, libDisk, datetime, sys

def main():
    disk = libTinyFS.tfs_mkfs("test.txt", 10240)
    print("creating file system under test.txt")

    libTinyFS.tfs_mount("test.txt")
    file1 = libTinyFS.tfs_open("foo.txt")
    libTinyFS.tfs_write(file1, bytes("hello there", encoding="utf8"), 11)

    file2 = libTinyFS.tfs_open("bar.txt")
    libTinyFS.tfs_write(file2, bytes("goodbye", encoding="utf8"), 8)

    print("printing from file 1: ", end = '')
    for x in range(0, 11):
        success, data = libTinyFS.tfs_readByte(file1)
        print(data)

    print("printing from file 2: ", end = '')
    for x in range(0, 8):
        success, data = libTinyFS.tfs_readByte(file2)
        print(data)


    libTinyFS.tfs_close(file1)

if __name__ == "__main__":
    main()