# Circom Analyzer

This repo hosts a translator from Circom to C.

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

The library of Vanguard for Aleo provides common vulnerability detectors and basic utilities for writing detectors based on static analysis. There are three ways to use and integrate the tool into your workflow, namely: commandline executable, calling from source and calling as library.

### Commandline Executable

The analyzer can be installed via `pip` setup tools by running:

```bash
pip install .
```

and if you want to remove it:

```bash
pip uninstall circom-analyzer
```

After installation, you can directly use the commandline executable `circom-analyzer` provided and get:

```bash
test run
```

#### Example Commands

To run the translator, in the translator folder:
```bash
cd ./translator/circom/backend/
python translator.py <path to circom file>
```

The generated C files will be in the same directory as the circom source file.

### Calling from Source

TODO

### Calling as Library

The analyzer can be installed via `pip` setup tools by running:

```bash
pip install .
```

and if you want to remove it:

```bash
pip uninstall vanguard
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
antlr4 -v 4.13.1 -Dlanguage=Python3 ./ CircomParser.g4 # generate parser
```

The parser/lexer file is located in `./translator/circom/parser/CircomLexer.g4` and `./translator/circom/parser/CircomParser.g4`.

To run the parser on a test Circom program `demo.circom`:

```bash
python test_circom.py
```

## Test Suite and Static Analysis APIs

(Coming soon...)
