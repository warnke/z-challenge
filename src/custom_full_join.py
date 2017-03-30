#!/usr/bin/env python3

class CustomJoin():
    
    def __init__(self, alternate_spellings_file = '../data/district_alternate_spellings.csv', 
                       phem_file = '../data/phem_sample_clean.csv', 
                       hmis_file = '../data/hmis_sample_clean.csv',
                       output_file = '../output/joined_table.csv'):
        
        # set filenames
        self.alternate_spellings_file = alternate_spellings_file
        self.phem_file = phem_file
        self.hmis_file = hmis_file
        self.output_file = output_file
        
        # initialize data structures
        self.alternate_spellings = dict()
        self.hmis_array = [] # holds rows of hmis table
        self.phem_array = [] # holds rows of phem table
        
        self.hmis_positions = dict() # key: (district, year, month) value: (corresponding row number in hmis_array)
        self.phem_positions = dict() # key: (district, year, month) value: (corresponding row number in phem_array)
               
        self.joined_table_header = []
        self.joined_table = []
        
        self.hmis_header_row = []
        self.phem_header_row = []
        
        self.hmis_row_len = 0
        self.phem_row_len = 0
        
    def parse_alternate_spellings(self):
        # - district itself always in the list of matches? No! -> add district to set as well.
        # - check if two (Region,Zone) tuples have the same District, i.e. need to check if District is unique or not
        #   --> This is indeed the case! Aregoba is an example for a non-unique key
        #       Workaround: include region and zone to the key, make it a tuple: (region, zone, district)
        
        '''
        Parses alternate spellings file and populates the class dictionary
        '''
        
        file = open(self.alternate_spellings_file, 'r')
        
        # get column names, remove newline character
        col_names = file.readline().split(",")
        col_names[-1] = col_names[-1].strip()
        
        for line in file:
            li = line.split(',')
            li[-1] = li[-1].strip()
            
            ## DEBUG: check if a key already exists!
            if (li[0], li[2]) in self.alternate_spellings:
               print("PANIC! Key {} already in dict".format((li[0],li[2])))
               break
            ##
            
            # initialize set for new key, key is a 3-tuple with (region, zone, district)
            self.alternate_spellings[(li[0], li[1], li[2])] = set()
            
            for i in li[2:]:
                if i == '':
                    continue
                # lower case version gets more matches
                i_lower = i.lower()
                self.alternate_spellings[(li[0], li[1], li[2])].add(i_lower)
                #self.alternate_spellings[(li[0], li[2])].add(i)
        file.close()


    def get_default_spelling(self, some_district_spelling):
        '''
        input: string, some district name in some spelling
        output: returns the default spelling of that district
        NOTE: In this first version, I am assuming that
              the default district names are unique which is not entirely true,
              i.e. only the 3-tuples (Region, Zone, District) are truly unique
              across the dataset. What I am doing for now: I simply return the first
              match and ignore the identity resolution problem for now. 
        NOTE: if no default spelling is found (perfect match), then original
              spelling is returned
        NOTE: could do fuzzy matching or Levenshtein distance to match, but
              that would be a bit arbitrary and could lead to false positives
              in short words.
        '''
        for key, value in self.alternate_spellings.items():
            if some_district_spelling.lower() in value:
            #if some_district_spelling in value: 
                return key[2]
        
        # ideally: catch an exception and log event if no district is found,
        # print('WARNING: no default spelling found for {}. Keeping original.'.format(some_district_spelling))
        return some_district_spelling

    
    def parse_hmis(self):
        '''
        input: hmis file
        output: void, populates 2d-list containing the rows of the hmis file
                and populates hmis_positions dictionary linking key and array positions
                also creates the hmis header row
                
        NOTE: li[3] = region (not used for now)
              li[4] = district
              li[14] = month (ethiopian)
              li[15] = year (ethiopian)
        '''
        
        file = open(self.hmis_file, 'r')
        
        # get column names, remove newline character
        col_names = file.readline().split(",")
        col_names[-1] = col_names[-1].strip()
        
        self.hmis_row_len = len(col_names)
        
        for col in col_names:
            self.hmis_header_row.append(col + " (HMIS)")
        
        rownum = 0
        for line in file:
            li = line.split(',')
            li[-1] = li[-1].strip()
            
            # replace district name with default district name
            #li[4] = self.get_default_spelling(li[4].lower())
            li[4] = self.get_default_spelling(li[4])
            
            self.hmis_array.append(li)
            # store rownum in dict
            if (li[4], li[15], li[14]) in self.hmis_positions:
                self.hmis_positions[(li[4], li[15], li[14])].append(rownum)
                # log: 'WARNING: hmis, more than one row belongs to the same key'
                # why is that? several different facilities can be in the same region/district
                # and contribute to the same database in the same month
                # ideally, we would aggregate over them, the percentage is small, ignoring this problem 
                # in version 1.0
            else:
                self.hmis_positions[(li[4], li[15], li[14])] = [rownum]
            rownum +=1
            
        file.close()
        
        
    def parse_phem(self):
        '''
        input: phem file
        output: void, populates 2d-list containing the rows of the phem file
                and populates phem_positions dictionary linking key and array positions
                
        NOTE: li[0] = region
              li[2] = district
              li[-2] = month (ethiopian)
              li[-1] = year (ethiopian)
        '''

        file = open(self.phem_file, 'r')
        
        # get column names, remove newline character
        col_names = file.readline().split(",")
        col_names[-1] = col_names[-1].strip()
        
        self.phem_row_len = len(col_names)
        
        for col in col_names:
            self.phem_header_row.append(col + " (PHEM)")
        
        rownum = 0
        for line in file:
            li = line.split(',')
            li[-1] = li[-1].strip()
        
            # replace district name with default district name
            # keep original if no default spelling is found
            li[2] = self.get_default_spelling(li[2])

            self.phem_array.append(li)
            
            # store rownum in dict
            if (li[2], li[-1], li[-2]) in self.phem_positions:
                self.phem_positions[(li[2], li[-1], li[-2])].append(rownum)
                # log: 'WARNING: phem, more than one row belongs to the same key'
                # why is that? several different districts can be in the same region/zone
                # and contribute to the same database in the same month
                # this does not happen very often. for now i append the rownum to a list
                # which will create slightly redundant data after the full outer join,
                # but prevent the loss of data
            else:
                self.phem_positions[(li[2], li[-1], li[-2])] = [rownum]
            rownum += 1
            
        file.close()
        
        

    def perform_full_outer_join(self):
        '''
        void, generates joined table array
        '''
      
        # Explain why phem_v and hmis_v are arrays: In several cases, a given district name occurs in different
        # regions. Therefore, when we key by default district name, year, data, we can have more than one
        # matching line. I have decided to iterate through the lines with identical keys for in both, the hmis
        # and the phem file. This creates slightly redundant data in the outer join, but it also prevents from
        # data loss.
        
        
        # if more than one value in value-array, we have multiple
        # rows that belong to the same key -> conflict. 
        # Could pick one and lose data, or pick all and have some redundant data - which behavior desired?
        # This only happens for a small portion of rows
        
        for hmis_k, hmis_v in self.hmis_positions.items():
            first_two_cols = [hmis_k[0], str(hmis_k[1]) + '-' + str(hmis_k[2])]

            if hmis_k in self.phem_positions:
                for ii in hmis_v:
                    for jj in self.phem_positions[hmis_k]:
                        self.joined_table.append(first_two_cols + self.hmis_array[ii] 
                                                                + self.phem_array[jj])
            else:
                for ii in hmis_v:
                    self.joined_table.append(first_two_cols + self.hmis_array[ii] + [''] * self.phem_row_len)
                
        for phem_k, phem_v in self.phem_positions.items():
            first_two_cols = [phem_k[0], str(phem_k[1]) + '-' + str(phem_k[2])]
            if phem_k not in self.hmis_positions:
                for ii in phem_v:
                    self.joined_table.append(first_two_cols + [''] * self.hmis_row_len + self.phem_array[ii]) 
                    

    def create_joined_table_header_row(self):
        self.joined_table_header = ['District Name', 'Date'] + self.hmis_header_row + self.phem_header_row
    
    def write_result(self):
        file = open(self.output_file, 'w')
        
        # write header
        header_string = ", ".join([str(i) for i in self.joined_table_header])
        file.write(header_string + '\n')

        # write rows
        for row in sorted(self.joined_table):
            row_string = ", ".join([str(i) for i in row])
            file.write(row_string + '\n')
            
        file.close()


if __name__ == "__main__":

    cj = CustomJoin()
    cj.parse_alternate_spellings()
    cj.parse_hmis()
    cj.parse_phem()
    cj.perform_full_outer_join()
    cj.create_joined_table_header_row()
    cj.write_result()

