import os
from translator.circom.run import translate

def main():
    directory = './zrepair-benchmarks/circom/circomlib-d1/'
    
    options = {
        'return_input': True,
        'return_output': True,
        'return_signal': True,
        'return_var': True,
        'return_public': True,
        'return_private': True,
        'return_intermediate': True,
        'return_c_files': True
    }

    for filename in os.listdir(directory):
        if filename.endswith('.circom'):
            file_path = os.path.join(directory, filename)
            print(f'Processing: {file_path}')
            # try:
            translate(
                    file_path,
                    **options
                )
            # except Exception as e:
                # print(f' {filename} Error: {str(e)}')

if __name__ == "__main__":
    main()