#from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection
from collections import defaultdict

# def main():
#   with open("output/prefix_sequence_user_pos.txt","r") as datafile:
#     data = datafile.read()
#   patterns = prefixSpan.parserSequence(data) 
#   subsumption_tree = create_subsumption_lattice(patterns)
#   print(subsumption_tree)


def create_subsumption_lattice(patterns):
  subsumption_tree = defaultdict(set)
  mapping_by_len = group_by_len(patterns)
  max_len = max(mapping_by_len.keys())
  attribute_mapping = make_attribute_mapping(patterns)

  for l in range(max_len-1): # maximal are not subsumed by anything
    print('processing len', l)
    sequences_with_len_l = mapping_by_len[l]
    for seq in sequences_with_len_l:
      sequences_with_len_l_plus_1 = mapping_by_len[l+1]
      with_at_least_the_same_attributes = get_attribute_intersection(seq, attribute_mapping)
      candidates = sequences_with_len_l_plus_1.intersection(with_at_least_the_same_attributes)
      for candidate in candidates:
        if is_seq1_subsumed_by_seq2(seq.get_attributes(),candidate.get_attributes()):
          subsumption_tree[candidate].add(seq)

  return subsumption_tree
  
# print mapping_by_len
# print attribute_mapping
  
  
def is_seq1_subsumed_by_seq2(attr1, attr2):
  max_l1 = len(attr1)
  max_l2 = len(attr2)
  i = 0
  j = 0
  while i < max_l1:
    if j >= max_l2:
      return False
    if attr1[i] == attr2[j]:
      i += 1
      j += 1
    else:
      j += 1
  return True

if __name__ == "__main__":
  main()