
# MarkyMark (mnm)
A versatile utility for converting various file types to Markdown format, making it easy to include 
code, CSV data, JSON, and other files in your Markdown documents. There are `<!-- file foo.txt-->` and
`<!--file end-->
<!-- No files found matching pattern 'end' -->
<!--file end-->
```

Would be written back into the file as a python MarkDown block.

```text
<!--file factorial.py-->
<!-- No files found matching pattern 'factorial.py' -->
<!--file end-->
```


It is worth noting that if there is any text between these start/end tags, and you rerun the tool the file
will be updated...however these blocks may not be recursive.

## Overview
MarkdownMaker (mnm) converts different file types to properly formatted markdown, supporting:
- Code files (.py, .java, .js, and many more)
- CSV files (with table formatting)
- JSON files (with syntax highlighting)
- Markdown files (pass-through with optional timestamp)
- Text files (plain text conversion)

**USEFUL NOTE: Paths are relative to the file that you are processing, so if files are in other folders please
reference them to the markdown file that you are reading from.**

## Installation
``` bash
# Clone the repository
git clone https://github.com/yourusername/markymark.git
cd markymark

# Install the package
pip install -e .
```
## Basic Usage


The basic command for converting files is:
``` bash
python -m mnm [FILE_PATH] [OPTIONS]
```
If you don't specify a file, it defaults to `../README.md`.
### Command Line Options
``` bash
# Convert a file and print to stdout
python -m mnm README.py

# Convert without adding a timestamp
python -m mnm README.md --no-date-stamp

# Disable automatic line breaks in CSV headers
python -m mnm README.md --no-auto-break
```
## Examples
### CSV to Markdown Table Conversion
#### Original CSV File: `sales_data.csv`
``` 
Region,Q1 Sales,Q2 Sales,Q3 Sales,Q4 Sales,Total
North,125000,133000,158000,175000,591000
South,105000,130000,115000,163000,513000
East,143000,123000,132000,145000,543000
West,117000,142000,138000,162000,559000
Total,490000,528000,543000,645000,2206000
```
#### Markdown Document with Inclusion: `report.md`
``` markdown
# Quarterly Sales Report

## Regional Sales Data

Here's a breakdown of our quarterly sales by region:

<!--file sales_data.csv-->
<!--file end-->

As we can see from the data, Q4 had the strongest performance across all regions.
```
#### After Running MarkdownMaker:
``` bash
python -m mnm convert report.md --bold "Total" -o final_report.md
```

---

#### Resulting Markdown: `final_report.md`

# Quarterly Sales Report

## Regional Sales Data

Here's a breakdown of our quarterly sales by region:

| Region | Q1 Sales | Q2 Sales | Q3 Sales | Q4 Sales | Total |
|--------|----------|----------|----------|----------|-------|
| North | 125000 | 133000 | 158000 | 175000 | 591000 |
| South | 105000 | 130000 | 115000 | 163000 | 513000 |
| East | 143000 | 123000 | 132000 | 145000 | 543000 |
| West | 117000 | 142000 | 138000 | 162000 | 559000 |
| **Total** | **490000** | **528000** | **543000** | **645000** | **2206000** |


As we can see from the data, Q4 had the strongest performance across all regions.

---

### Including JSON Configuration
``` markdown
## Configuration

The default configuration is:

<!--file path/to/config.json-->
<!--file end-->
```
## File Type Support
MarkdownMaker supports numerous file extensions allowing MarkDown to correctly syntax highlight:
- Python: `.py`, `.pyw`, `.pyx`, `.pyi`
- JavaScript: `.js`, `.mjs`, `.cjs`
- TypeScript: `.ts`, `.tsx`
- Java: `.java`
- C/C++: `.c`, `.h`, `.cpp`, `.cc`, `.hpp`
- Web: `.html`, `.htm`, `.css`, `.scss`
- Data: `.json`, `.yaml`, `.yml`, `.csv`
- Configuration: `.ini`, `.cfg`, `.conf`
- Shell: `.sh`, `.bash`, `.zsh`
- And many more!

## Options for CSV Files
When converting CSV files, you have additional options:
- `--bold VALUE1,VALUE2,...` - Make specific columns bold in the table
- `--auto-break/--no-auto-break` - Control automatic line breaks in CSV headers

## Examples

### Help

```text
(.venv) chuck@Chucks-Mac-mini markymark % python mnm.py --help
                                                                                                                                                                                                                                                                                                                                                                                   
 Usage: mnm.py [OPTIONS] [FILE_NAME]                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                   
 Convert a file to Markdown based on its extension.                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                   
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   file_name      [FILE_NAME]  The file to convert to Markdown [default: ../README.md]                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output              -o                     TEXT  Output file (if not specified, prints to stdout) [default: None]      │
│ --bold                -b                     TEXT  Comma-separated values to make bold (for CSV files) [default: None]   │
│ --auto-break              --no-auto-break          Disable automatic line breaks in CSV headers [default: auto-break]    │
│ --help                                             Show this message and exit.                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### UV Run
It wouldn't be an example unless we showed you that you can run `mnm` with `uv` without knowing anything beyond
installing `uv` on your machine by taking advantage of support for [PEP 723](https://peps.python.org/pep-0723/). 

ASSUMING that you have `uv` installed on your machine and that you have `mnm.py installed on your machine

This is the recommended way of using `mnm`.

```bash
uv run mnm.py ../README_template.md --output ../README.md
````



### Convert a CSV file with bold totals
``` bash
python -m mnm sales_data.csv --bold "Total,Sum" -o sales_report.md
```
### Update embedded references in a markdown file
``` bash
python -m mnm documentation.md -o updated_docs.md
```
## License
[MIT License](LICENSE)
