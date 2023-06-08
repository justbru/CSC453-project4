import libTinyFS, libDisk, datetime, sys

def main():
    disk = libTinyFS.tfs_mkfs("test.txt", 10240)
    print("creating file system under test.txt")
    libTinyFS.tfs_mount("test.txt")
    file1 = libTinyFS.tfs_open("foo.txt")
    libTinyFS.tfs_write(file1, bytes("hello thereeeeeeeeeeeeeeeeeeeeeeeeeeee", encoding="utf8"), 256)
    print(libTinyFS.tfs_readByte(file1))
    print(libTinyFS.tfs_readByte(file1))
    print(libTinyFS.tfs_readByte(file1))
    print(libTinyFS.tfs_readByte(file1))
    print(libTinyFS.tfs_readByte(file1))
    print(libTinyFS.tfs_readByte(file1))
    libTinyFS.tfs_close(file1)

if __name__ == "__main__":
    main()