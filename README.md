# FREE ADSL Bill fetcher

#### Table of Contents

1. [Overview](#overview)
2. [Instructions](#instructions)
    * [How to install](#how_to_install)
    * [How to configure](#how_to_configure)
    * [How to use](#how_to_use)
3. [Development - Guide for contributing](#development)

## Overview

This software was created to retrieve FREE telecom bills in an easy way.

## Instructions

### How to install

```
$ git clone git@github.com:riton/free_adsl_bill_fetcher.git
$ pip install -r free_adsl_bill_fetcher/requirements.txt
```

_Note_: `lxml` library requires `libxslt-dev` and `libxml2-dev`

### How to configure

Software configuration file defaults to `~/.free_adsl_bill_fetcher.conf`.

**Example**:

```json
{
    "login": "TheLog1n",
    "password": "thePassw0rd"
}
```

#### `login`

Your FREE telecom username.

#### `password`

Your FREE telecom account password.

### How to use 

```
Usage: free_adsl_bill_fetcher [options]

Options:
  -h, --help            show this help message and exit
  -p, --show-price      show price when listing bills
  --latest              only fetch latest bill
  -c FILE, --config=FILE
                        configuration file
  --get=BILL_TITLE      Download bill BILL_TITLE and write it as
                        BILL_TITLE.pdf
  -d DIR, --write-dir=DIR
                        write bills to directory DIR
  --name-prefix=STR     prefix each bill filename with STR
  --name-suffix=STR     suffix each bill filename with STR (before PDF
                        extension)
```

**Retrieve latest bill**

```
$ free_adsl_bill_fetcher --latest
Your latest bill was written to './Octobre_2014.pdf'
```

**List all available bills with their price**

```
$ free_adsl_bill_fetcher -p
+----------------+---------+
| Month          |  Price  |
+----------------+---------+
| Octobre 2014   | 12 €    |
| ...            | ....... |
+----------------+---------+
```

**Retrieve multiple specific bills**

```
$ free_adsl_bill_fetcher --get='Août 2014' --get='Août 2013'
[*] Août 2014 bill was written to './Août_2014.pdf'
[*] Août 2013 bill was written to './Août_2013.pdf'
```

**Add suffix and/or prefix to bills names**

```
$ free_adsl_bill_fetcher --get='Août 2014' --get='Août 2013' --name-prefix="Ferrand_Remi_" --name-suffix="_Facture_ADSL"
[*] Août 2014 bill was written to './Ferrand_Remi_Août_2014_Facture_ADSL.pdf'
[*] Août 2013 bill was written to './Ferrand_Remi_Août_2013_Facture_ADSL.pdf'
```

## Development - Guide for contributing

Please submit a Pull Request / Merge request if you want to contribute to this project.
