def error_exit(err_type):
    match err_type:

        case -16:
            print("EDISKSIZEALLOC: Disk Size Allocation Parameter is not evently divisible by block size")
            exit(-16)
        case -17:
            print("EFILE: File could not be opened")
            exit(-17)
        case -18:
            print("ESEEK: File seeking failed")
            exit(-18)
        case -19:
            print("EREAD: Failed to read file")
        case -20:
            print("EWRITE: Failed to write to file")
        case -21:
            print("ECLOSE: Failed to close file")
        case -22:
            print("EBITMAP: Bitmap is too large for superblock bounds")
            exit(-22)
        case -23:
            print("EFILENAMELEN: Filename is too large")
            exit(-23)
        case -24:
            print("ENOTFS: Given filename is not initialized as a file system")
            exit(-24)
        case -25:
            print("ENOMOUNTEDFS: No currently mounted file system")
            exit(-25)
        case -26:
            print("EFILEPOINTER: File pointer is at end of file. Cannot read further.")
        case -27:
            print("EFILENOTOPEN: File is not open. Failed to write")
        case default:
            print("Unexpected Error")
            exit(-400)