
#!/usr/bin/env python

"""mefdas.py: Description of what foobar does."""

__author__      = "Philip Chase(pbc@ufl.edu, Chris Barnes(cpb@ufl.edu), Roy Keyes (keyes@ufl.edu), Alex Loiacono (atloiaco@ufl.edu)"
__copyright__   = "Copyright 2015, CTS-IT University of Florida"


class fuzzyMeasure:
    '''A class to produce a fuzzy measure of based on a list of criteria'''

    def __init__(self, number_of_criteria):
        # build a data structure to hold all possible subsets of a set of size = number_of_criteria
        self.data = []
        #self.data = make_all_subsets(1..number_of_criteria)

    def make_all_subsets(list_of_members):
        # make every possible subsets of given list_of_members
        # for size in (list_of_members):
            # use combinations to enumerate all combinations of size elements
            # append all combinations to self.data

    def set_fm_for_trivial_cases(self):
        # set fuzzyMeasure for empty and complete sets
        # mu(∅) := 0
        # mu(X) := 1

    def set_fm_for_singleton_sets(self):
        # set fuzzyMeasure for sets with exactly one member

    def set_fm_for_complex_sets(self):
        # set fuzzyMeasure for sets with 2 or more members

        # Random generation of a fuzzy measure mu on a set X
        # note: 'undefined' means we have not yet calculated and stored the value of mu for mu(foo)
        # create list of sets from X
        # shuffle list of sets of X
        # for each A in shuffled_list_X:
            # if mu(A) is undefined:
                # min := 0
                # max := 1

                # subsets_of_A = make_all_subsets(A)
                # for each B in subsets_of_A:
                    # if mu(B) is defined:
                        # min = maximum(mu(B), min)

                # for each B in X:
                    # if mu(B) is defined:
                        # case B ⊃ A :
                            # max = minimum(max, mu(B))
                            # break
                        # case other:
                            # do nothing
                    # else:
                        # mu(B) is undefined so do nothing
                # mu(A) := random value between min and max


if __name__ == "__main__":
    import sys
    mefdas(int(sys.argv[1]))