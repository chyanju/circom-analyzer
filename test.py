from translator.circom.run import translate

def main():
    file_name = './tests/examples/IsZero/circom/is-zero.circom'
    return_input = True
    return_output = True
    return_signal = True
    return_var = True
    return_public = True
    return_private = True
    return_intermediate = True
    return_c_files = True

    translate(file_name, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, return_c_files)

if __name__ == "__main__":
    main()