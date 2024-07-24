# Circom Analyzer

This repo hosts a translator from Circom to C.

For signal arrays, this tool only return the name of the array.

## Table of Contents

- [Circom Analyzer](#circom-analyzer)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Commandline Executable](#commandline-executable)
      - [Example Commands](#example-commands)
    - [Calling from Source](#calling-from-source)
    - [Calling as Library](#calling-as-library)
  - [Detectors Available](#detectors-available)
  - [Example Circom Vulnerabilities](#example-circom-vulnerabilities)
  - [Parser/Lexer Generation](#parserlexer-generation)
  - [Test Suite and Static Analysis APIs](#test-suite-and-static-analysis-apis)

## Prerequisites

The following libraries are required for running (different components of) the tool:

- Python (3.10+) for running the parser and the translator
  - [Antlr](https://www.antlr.org/) (4.13.1) and its Python binding for loading and parsing Aleo programs
    - `pip install antlr4-python3-runtime==4.13.1`
    - `pip install antlr4-tools`
  - [tabulate](https://github.com/astanin/python-tabulate) (0.9.0+) for result table rendering

## Usage

The library of Circom Analyzer provides a translator from Circom to C and basic utilities for returning public/private/intermediate input/output signal/var for a Circom program. There are three ways to use and integrate the tool into your workflow, namely: commandline executable, calling from source and calling as library.

### Commandline Executable

The analyzer can be installed via `pip` setup tools by running:

```bash
pip install .
```

and if you want to remove it:

```bash
pip uninstall circom-analyzer
```

After installation, you can directly use the commandline executable `circom-analyzer` provided:

```bash
usage: circom-analyzer [-h] [--input INPUT] [--ins] [--outs] [--s] [--v] [--pub] [--pri] [--inter] [--c]

Circom translator that converts Circom to C, with options to output specific signals or variables to a JSON file.

options:
  -h, --help     show this help message and exit
  --input INPUT  input Circom file path
  --ins          return input signals
  --outs         return output signals
  --s            return all signals
  --v            return variables
  --pub          return public signals
  --pri          return private signals
  --inter        return intermediate signals
  --c            generate C files
```

#### Example Commands

- To run the translator and simply generate C files from a Circom file:
  ```bash
  circom-analyzer --input ./tests/examples/Decoder/circom/Decoder.circom --c
  ```
  The generated C files will be in the same directory as the circom source file.

- To simply return all signals from a Circom file:
  ```bash
  circom-analyzer --input ./tests/examples/Decoder/circom/Decoder.circom --s
  ```

- To run the translator and return all signals from a Circom file:
  ```bash
  circom-analyzer --input ./tests/examples/Decoder/circom/Decoder.circom --s
  ```
- To run the translator and get all information:
  ```bash
  circom-analyzer --input ./tests/examples/IsZero/circom/is-zero.circom --pub --inter --pri --s --ins --outs --v --c
  ```
  and you will get whe following JSON file in the same directory as the circom source file:
  ```json
  {
      "public": [
          "out"
      ],
      "private": [
          "in"
      ],
      "intermediate": [],
      "input": [
          "in"
      ],
      "output": [
          "out"
      ],
      "signal": [
          "in",
          "out"
      ],
      "var": []
  }
  ```


### Calling from Source

TODO

### Calling as Library

The analyzer can be installed via `pip` setup tools by running:

```bash
pip install .
```

and if you want to remove it:

```bash
pip uninstall circom-analyzer
```

TODO

## Detectors Available

TODO

## Example Circom Vulnerabilities

TODO

## Parser/Lexer Generation

In case the parser is not compatible with your environment, you can generate it again using Antlr:

```bash
cd ./translator/circom/parser/
antlr4 -v 4.13.1 -Dlanguage=Python3 ./CircomLexer.g4 # generate lexer
antlr4 -v 4.13.1 -Dlanguage=Python3 ./CircomParser.g4 # generate parser
```

The parser/lexer file is located in `./translator/circom/parser/CircomLexer.g4` and `./translator/circom/parser/CircomParser.g4`.

To run the parser on a test Circom program `demo.circom`:

```bash
python test_circom.py
```

## Test Suite and Static Analysis APIs

(Coming soon...)
