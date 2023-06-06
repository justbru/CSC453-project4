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
            exit(-19)
        case -20:
            print("EWRITE: Failed to write to file")
            exit(-20)
        case -21:
            print("ECLOSE: Failed to close file")
            exit(-21)
        case default:
            print("Unexpected Error")
            exit(-400)