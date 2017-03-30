# Joining tables

## ToDos
See Repo Issues

## Overview and Notes
* Full outer join
* I key by default district name and date
* A given key often only exists in one of the two files. If this is the case, the resulting row only contains information from one file,
  the rest is null (empty strings)
* The default district name is not always included in list match0, .... I added the default district name to the list of matches as well
* Many district names from the phem and hmis input files cannot be mapped to a default mapping. I decided to only compare lower case strings
  which slightly increases the number of matches
* Possible to do fuzzy matching or to use the Levenshtein distance to decide if two strings are treated as identical, but could lead to
  false positives and possibly to loss of information. Fuzzy matching outside of the scope of the project, needs to be discussed with client first
* A given (District name, date) key tuple is not necessarily unique, i.e. two rows in same file can have identical key.
  * Example: 

             phem-file: row a = ("district a", "date 123", ... some data) exists together with
                        row b = ("district a", "date 123", ... some other data)
             hmis-file: row c = ("district a", "date 123", ... some hmis data ...)

             resulting rows: (row a + row c,
                              row b + row c)

    When matching two rows from phem-file to one row from hemis-file (for example),
    I create the same hemis-file row portion twice and add a corresponding
    rows from the phem file to each of them. In this case I create slightly redundant data instead of potentially discarding data, which
    might not be acceptable.

## Dependencies
* I am using python 3 
* Only std library functions needed
* I am doing everything on foot, I am not using any dataframe libraries like Pandas

## Usage
* Change to src directory (important, because current version uses relative paths only)
* Make file executable `chmod u+x custom_full_join.py`
* Execute `./custom_full_join.py`
* result file written into output directory


