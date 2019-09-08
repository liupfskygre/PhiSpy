import os
import re
import math
import string
import pprint
import sys
import array


class ShannonScore:
     """
        To measure the abundance of phage ‘words’, Shannon’s
        index (19,20) and the frequency of the presence of phage
        words were calculated.
        Shannon’s index was calculated by the following
        formula:
        H = - SUMi(pi * log(pi))
        where pi is the frequency of those words which are
        present in the ‘phage word library’. The frequency of
        words (F) of a window was calculated by dividing the
        number of available phage words with the total number
        of words. For a given window, the abundance of phage
        words is F/H
     """

     def __init__(self,INSTALLATION_DIR):
          # Create a hash of the kmers that points to the index of an array that holds the value
          self._key_to_index = {}
          self._values_ = array.array('i')
          self.total = 0
          self._kmers_phage = []
          self._kmers_all = []
          try:
               infile = open(INSTALLATION_DIR+'data/mer_ORF_list.txt','r')
          except:
               sys.exit('ERROR: Cannot open data/mer_ORF_list.txt')
          for line in infile:
               line = line.strip()
               # self._values.append(0) # the size of mer_ORF_list lines number
               self._key_to_index[line] = '' # len(self._values) - 1 # kept the index of referring selv._values
     def reset(self):
          self.total = 0
          #self._values = array.array('i', '\x00'*self._values.itemsize*len(self._values))
          self._values = array.array('i', [0] * len(self._values))
     def addValue(self, seq):
          # it checks how many phage-like 12-mers are present in each gene -> stored in self._values[]
          mer = 12
          seq = seq.strip().upper()
          pos = 0
          # if len(self._kmers_phage) < 20: print('seq:', len(seq))
          self._kmers_phage.append(0)
          self._kmers_all.append(0)
          while( pos <= (len(seq) - mer) ):
               substr = seq[pos:pos+mer]
               pos = pos + mer
               # if substr in self._key_to_index:
                    # self._values.[self._key_to_index[substr]] += 1 # {0: 5, 1: 20, 2:0}
               self._kmers_all[-1] += 1 
               try:               
                    self._key_to_index[substr]
                    self._kmers_phage[-1] += 1
                    # if len(self._kmers_phage) < 21:print(1)
               except KeyError:
                    continue
               # self.total += 1
     def getSlope(self, start, stop):
           total = sum(self._kmers_all[start : stop])
           found_total = sum(self._kmers_phage[start: stop])
           # print(found_total, total)
           # if self.total ==0: # total number of mers identified within the analyzed window
           if total == 0:
                 return 0
           H = 0.0
           # cnt = 0
           p = 1 / total
           for i in range(found_total): #self._key_to_index: # read all 100k mers
                 # p = float(self._values[self._key_to_index[i]])/self.total # the p of certain mers number within analyzed window / all mers identified within windown
                 # p = float(self._kmers_phage[i])/total
                 # if( p > 0 ):
                       # print(p)
                       # cnt += self._kmers_phage[i]
                 H = H + p * (math.log(p)/math.log(2))
                       # found_total += self._values[self._key_to_index[i]]
                       # found_total += self._values[i]

           # H = -H
           if H > 0:
                 return 0
           # freq_found = found_total/float(self.total)
           freq_found = found_total/float(total)
           myslope = -freq_found/H
           # print('aaaa', cnt, myslope, 'bbbb', start, stop, len(self._key_to_index))
           # exit()
           return myslope

def read_contig(organismPath):
     try:
          f_dna = open(organismPath+'/contigs','r')
     except:
          print('cant open contig file ',organismPath)
          return ''
     dna = {}
     seq = ''
     name = ''
     for i in f_dna:
          if i[0]=='>':
               if len(seq)>10:
                    dna[name]=seq
               name = i.strip()
               if ' ' in name:
                    temp = re.split(' ',name)
                    name = temp[0]
               name = name[1:len(name)]
               seq = ''
          else:
               seq = seq+i.strip()
     dna[name]=seq
     f_dna.close()
     return dna

def read_genbank(organismPath):
    try:
        f_dna = open(organismPath,'r')
    except:
        print('cant open genbank file ',organismPath)
        return ''
    dna = {}
    peg = {}
    seq = ''
    name = ''
    for line in f_dna:
        if line.startswith('LOCUS '):
            dna[name] = seq    
            name = line.split()[1]
            peg[name] = {}
        elif line.startswith('ORIGIN'):
            line = next(f_dna)
            while not line.startswith('//'):
                seq += ''.join(line.split()[1:])
                line = next(f_dna)
        elif line.startswith('     CDS '):
            x = len(peg[name])
            peg[name][x] = {}
            loc = ''.join(c for c in line.split()[1] if c in '0123456789.,').replace('.',' ').replace(',',' ').split()
            #line.split()[1].replace('complement(','').replace(')') 
            if 'complement' in line:
                peg[name][x]['stop'] = int(loc[0])
                peg[name][x]['start'] = int(loc[-1])
            else:
                peg[name][x]['start'] = int(loc[0])
                peg[name][x]['stop'] = int(loc[-1])
            peg[name][x]['peg'] = name + "_" + loc[0] + "_" + loc[-1]
            peg[name][x]['is_phage'] = 0
        elif line.startswith('                     /is_phage='):
            x = len(peg[name])-1
            peg[name][x]['is_phage'] = int(line.split('=')[1])
    del dna['']
    dna[name] = seq    
    return dna, peg

def my_sort(orf_list):
     n = len(orf_list)
     i = 0
     while(i < n):
          j = i + 1
          while( j < n):
               flag = 0
               #direction for both
               if orf_list[i]['start']<orf_list[i]['stop']:
                    dir_i = 1
               else:
                    dir_i = -1
               if orf_list[j]['start']<orf_list[j]['stop']:
                    dir_j = 1
               else:
                    dir_j = -1
               #check whether swap need or not
               if dir_i == dir_j:
                    if orf_list[i]['start']>orf_list[j]['start']:
                         flag = 1
               else:
                    if dir_i == 1:
                         if orf_list[i]['start']>orf_list[j]['stop']:
                              flag = 1
                    else:
                         if orf_list[i]['stop']>orf_list[j]['start']:
                              flag = 1
               #swap
               if flag == 1:
                    temp = orf_list[i]
                    orf_list[i] = orf_list[j]
                    orf_list[j] = temp
               j += 1
          i += 1
     return orf_list

def find_all_median(x):
     all_len = []
     for i in x:
          all_len.append((abs(x[i]['start']-x[i]['stop']))+1)
     return find_median(all_len)

def find_median(all_len):
     n = int(round(len(all_len)/2))
     all_len.sort()
     if len(all_len) == n*2:
          return (all_len[n]+all_len[n-1])/float(2)
     else:
          return all_len[n]

def find_avg_length(orf_list):
     x = []
     for i in orf_list:
          x.append(abs(orf_list[i]['start']-orf_list[i]['stop']))
     return sum(x)/len(x)

def find_atgc_skew(seq):
     seq = seq.upper()
     total_at = 0.0
     total_gc = 0.0
     a = 0
     t = 0
     c = 0
     g = 0
     for base in seq:
          if base == 'A':
               a += 1
               total_at += 1
          elif base == 'T':
               t += 1
               total_at += 1
          elif base == 'G':
               g += 1
               total_gc += 1
          elif base == 'C':
               c += 1
               total_gc += 1
          elif base == 'R':
               a += 0.5
               total_at += 0.5
               g += 0.5
               total_gc += 0.5
          elif base == 'Y':
               c += 0.5
               total_gc += 0.5
               t += 0.5
               total_at += 0.5
          elif base == 'S':
               g += 0.5
               total_gc += 0.5
               c += 0.5
               total_gc += 0.5
          elif base == 'W':
               a += 0.5
               total_at += 0.5
               t += 0.5
               total_at += 0.5
          elif base == 'K':
               g += 0.5
               total_gc += 0.5
               t += 0.5
               total_at += 0.5
          elif base == 'M':
               c += 0.5
               total_gc += 0.5
               a += 0.5
               total_at += 0.5
          elif base == 'B':
               c += 0.3
               total_gc += 0.3
               g += 0.3
               total_gc += 0.3
               t += 0.3
               total_at += 0.3
          elif base == 'D':
               a += 0.3
               total_at += 0.3
               g += 0.3
               total_gc += 0.3
               t += 0.3
               total_at += 0.3
          elif base == 'H':
               a += 0.3
               total_at += 0.3
               c += 0.3
               total_gc += 0.3
               t += 0.3
               total_at += 0.3
          elif base == 'V':
               a += 0.3
               total_at += 0.3
               c += 0.3
               total_gc += 0.3
               g += 0.3
               total_gc += 0.3
          elif base == 'N':
               a += 0.25
               total_at += 0.25
               t += 0.25
               total_at += 0.25
               g += 0.25
               total_gc += 0.25
               c += 0.25
               total_gc += 0.25
          else:
               print("seq", seq)
               print("base", base)
               sys.exit("ERROR: Non nucleotide base found")
     if(total_at * total_gc) == 0:
          sys.exit("a total of zero")
     return float(a)/total_at, float(t)/total_at, float(g)/total_gc, float(c)/total_gc

def find_avg_atgc_skew(orf_list,mycontig,dna):
     a_skew = []
     t_skew = []
     g_skew = []
     c_skew = []
     for i in orf_list:
          start = orf_list[i]['start']
          stop = orf_list[i]['stop']
          if start<stop:
               bact = dna[mycontig][start-1:stop]
               xa, xt, xg, xc = find_atgc_skew(bact)
          else:
               bact = dna[mycontig][stop-1:start]
               xt, xa, xc, xg = find_atgc_skew(bact)
          if len(bact)<3:
               continue
          a_skew.append(xa)
          t_skew.append(xt)
          g_skew.append(xg)
          c_skew.append(xc)
     return a_skew, t_skew, g_skew, c_skew

######################################################################################

def make_set_train(trainSet,organismPath,output_dir,window,INSTALLATION_DIR):
     my_shannon_scores = ShannonScore(INSTALLATION_DIR)
     all_orf_list = {}
     dna, all_orf_list = read_genbank(organismPath)
     try:
          outfile = open(output_dir+trainSet,'a')
     except:
          sys.exit('ERROR: Cannot open file for writing:'+outfile)
     outfile.write('orf_length_med\tshannon_slope\tat_skew\tgc_skew\tmax_direction\tstatus\n')
     for mycontig in all_orf_list:
          orf_list = my_sort(all_orf_list[mycontig])
          ######################
          #avg_length = find_avg_length(orf_list)

          if not orf_list:
              continue

          all_median = find_all_median(orf_list)
          lengths = []
          directions = []
          for i in orf_list:
              lengths.append(abs(orf_list[i]['start']-orf_list[i]['stop'])+1) # find_all_median can be deleted now
              directions.append(1 if orf_list[i]['start'] < orf_list[i]['stop'] else -1)
              if orf_list[i]['start'] < orf_list[i]['stop']:
                   seq = dna[mycontig][orf_list[i]['start'] - 1 : orf_list[i]['stop']]
              else:
                   seq = dna[mycontig][orf_list[i]['stop'] - 1 : orf_list[i]['start']]
              my_shannon_scores.addValue(seq)

          ga_skew, gt_skew, gg_skew, gc_skew = find_avg_atgc_skew(orf_list,mycontig,dna)
          a = sum(ga_skew)/len(ga_skew)
          t = sum(gt_skew)/len(gt_skew)
          g = sum(gg_skew)/len(gg_skew)
          c = sum(gc_skew)/len(gc_skew)
          avg_at_skew, avg_gc_skew = math.fabs(a-t), math.fabs(g-c)
          #####################
          i = 0
          #while i<len(orf_list)-window +1:
          while(i < len(orf_list) ):
               #initialize
               j_start = i - int(window/2)
               j_stop = i + int(window/2)
               if (j_start < 0):
                   j_start = 0
               elif (j_stop >= len(orf_list)):
                      j_stop = len(orf_list)
               # at and gc skews
               ja_skew = ga_skew[j_start:j_stop]
               jt_skew = gt_skew[j_start:j_stop]
               jc_skew = gc_skew[j_start:j_stop]
               jg_skew = gg_skew[j_start:j_stop]
               ja = sum(ja_skew)/len(ja_skew)
               jt = sum(jt_skew)/len(jt_skew)
               jc = sum(jc_skew)/len(jc_skew)
               jg = sum(jg_skew)/len(jg_skew)
               jat = math.fabs(ja-jt)/avg_at_skew if avg_at_skew else 0
               jgc = math.fabs(jg-jc)/avg_gc_skew if avg_gc_skew else 0
               my_length = find_median(lengths[j_start:j_stop]) - all_median
               # my_shannon_scores.reset()
               for j in range(j_start, j_stop):
                    start = orf_list[j]['start']
                    stop = orf_list[j]['stop']
                    if start > stop: 
                        start, stop = stop, start
                    # my_shannon_scores.addValue(dna[mycontig][start - 1 : stop])
               # orf direction
               orf = []
               x = 0
               flag = 0
               for ii in directions[j_start:j_stop]:
                   if( ii == 1 ):
                       if( flag == 0 ):
                           x += 1
                       else:
                           orf.append(x)
                           x = 1
                           flag = 0
                   else:
                       if( flag == 1 ):
                           x += 1
                       else:
                           if( flag < 1 and x > 0 ):
                                orf.append(x)
                           x = 1
                           flag = 1
               orf.append(x)
               orf.sort()
               outfile.write(str(my_length))
               outfile.write('\t')
               outfile.write(str(my_shannon_scores.getSlope(j_start, j_stop)))
               outfile.write('\t')
               outfile.write(str(jat))
               outfile.write('\t')
               outfile.write(str(jgc))
               outfile.write('\t')
               outfile.write(str(orf[len(orf)-1]) if len(orf) == 1 else str(orf[len(orf)-1]+orf[len(orf)-2]))
               outfile.write('\t')
               outfile.write('1' if orf_list[i]['is_phage'] else '0')
               outfile.write('\n')
               i += 1
     outfile.close()

##################### function call #################################

def call_make_train_set(trainSet,organismPath,output_dir,INSTALLATION_DIR):
     window = 40
     try:
          outfile = open(output_dir+trainSet,'w')
     except:
          sys.exit('ERROR: Cannot open file for writing:'+outfile)
     outfile.close()
     make_set_train(trainSet, organismPath, output_dir, window, INSTALLATION_DIR)
     # Check whether the output file has data. For shorter genomes (less that 40 genes) phiSpy will not work)
     num_lines = sum(1 for line in open(output_dir+trainSet,'r'))
     if(num_lines > 0):
          return 1
     else:
          return 0


