# sarakstu2 Script Documentation

## Description
`sarakstu2` is a Bash script that processes a given text file (such as a log file) and extracts specific sections using `sed`.  
It is mainly designed to:
- Extract text between `GINC` and `ob cpu tim`, cleaning up formatting.
- Optionally extract the *non-standard PCM* section when requested.

## Usage
```bash
./sarakstu2 [-s] <filename>
```

### Arguments
- `<filename>` : Path to the input file to be processed.

### Options
- `-s` : Additionally extract the *non-standard PCM* section (between `Using the following` and `end of non-standard`).

## Examples
1. Process a file without non-standard PCM:
```bash
./sarakstu2 output.log
```

2. Process a file and include the non-standard PCM section:
```bash
./sarakstu2 -s output.log
```

## Notes
- The script prints the input filename before showing extracted content.
- Formatting cleanup includes:
  - Removing trailing `--`
  - Removing line breaks inside blocks
  - Cleaning up separator lines
