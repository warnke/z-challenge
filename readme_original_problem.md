# Joining two health databases

This code exercise is a very simplified example of one of the data problems our platform solves.  There's no strict time limit but you shouldn't spend more than an hour or so on it.  

The end result doesn't have to be fully functional or perfect, but it will give us an idea of what your code looks like in whatever language you prefer.  Good luck and have fun!

## Two databases with overlapping data

In this repository, there are two CSV "databases" in the `data/` folder.

`HMIS` is a sample of a general health management information system that records many general health indicators and their values.  `PHEM` is more focused on public health emergencies.  Both contain overlapping data.

Each database records the value of an indicator in a given geography, on a given date.  Both tables are *roughly* of the form:

| District Name   | Date recorded     | # Malaria Cases | # HIV Cases | # Tuberculosis Cases | ... |
|-----------------|-------------------|-----------------|-------------|----------------------|-----|
| foo             | 2016-01-01        | 5               | 8           | 12                   |     |
| bar             | 2016-01-01        | 3               | 2           | 9                    |     |
| bazz            | 2016-02-01        | 8               | 2           | 4                    |     |

However, you'll notice that the tables don't match.  If `HMIS` is the table above, then the `PHEM` table looks something like this.

| District   | Date     | Num. Malaria | New HIV Cases | TB recorded | ... |
|-----------------|-------------------|-----------------|-------------|----------------------|-----|
| Foo District    | 2016-01        | 0               | 1           | 3                   |     |
| A'Bar           | 2016-01        | 10               | 3           | 6                    |     |
| Baz             | 2016-02        | 4               | 4           | 8                    |     |

## Creating a "full integration"

We want to create a **full integration**, a combined table that represents *all* the data across the entire health system.  In order to do this, we need to join rows across **District name** and **Date**, producing a table like this one:

| District Name   | Date     | # Malaria Cases (HMIS) | # HIV Cases (HMIS) | # Tuberculosis Cases (HMIS) |  Num. Malaria (PHEM) | New HIV Cases (PHEM) | TB recorded (PHEM) | ... |
|-----------------|-------------------|-----------------|-------------|----------------------|-----|----|----|----|
| Foo             | 2016-01-01        | 5               | 8           | 12                   | 0               | 1           | 3                   |      |
| Bar             | 2016-01-01        | 3               | 2           | 9                    |  10               | 3           | 6                    |      |
| Baz             | 2016-02-01        | 8               | 2           | 4                    |  4               | 4           | 8                    |     |

You'll notice that in order to join the rows properly, you'll need a mapping from `Foo District -> Foo`, `bazz -> Baz`, and `A'Bar -> Bar`, etc.  This mapping is available in `district_alternate_spellings.csv`.  You should prefer the canonical spelling in the `District` column.

## In summary

**Inputs**:

  - HMIS CSV
  - PHEM CSV
  - Canonical District Mapping CSV

**Output**: Integration CSV
