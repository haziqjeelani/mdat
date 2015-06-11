
#!/usr/bin/env python

"""mdat.py: medical decision aid tool"""

__author__ = "Philip Chase(pbc@ufl.edu, Chris Barnes(cpb@ufl.edu), " \
             "Roy Keyes (keyes@ufl.edu), Alex Loiacono (atloiaco@ufl.edu)"
__copyright__ = "Copyright 2015, CTS-IT University of Florida"

import itertools
import random
import operator
import json
import jsonschema
import sys
import argparse

def make_all_subsets(list_of_members):
        # make every possible subsets of given list_of_members
        # for size in (list_of_members):
            # use combinations to enumerate all combinations of size elements
            # append all combinations to self.data

        set_of_all_subsets = set([])

        for i in range(len(list_of_members),-1,-1):
            for element in itertools.combinations(list_of_members,i):
                set_of_all_subsets.add(frozenset(element))

        return sorted(set_of_all_subsets)

class FuzzyMeasure:
    '''A class to produce a fuzzy measure of based on a list of criteria'''

    def __init__(self, criteria={}):
        # initialize a class to hold all fuzzyMeasure related objects
        self.set_of_all_subsets = set([])
        self.mu = ()
        self.criteria = criteria
        self.list_of_members = frozenset(criteria.keys())
        self.setup()

    def setup(self):
        if len(self.criteria) < 1 :
            return
        self.make_all_subsets()
        self.set_fm_for_trivial_cases()
        self.set_fm_for_singleton_sets()
        self.set_fm_for_complex_sets()

    def store_criteria(self, criteria):
        self.list_of_members = frozenset(criteria.keys())
        self.criteria = criteria

    def make_all_subsets(self):
        # make every possible subsets of given list_of_members
        self.set_of_all_subsets = make_all_subsets(self.list_of_members)

    def set_fm_for_trivial_cases(self):
        # set fuzzyMeasure for empty and complete sets
        # mu[] := 0
        # mu[X] := 1
        self.mu = {frozenset(): 0, self.list_of_members: 1}

    def set_fm_for_singleton_sets(self):
        '''set fuzzyMeasure for sets with exactly one member'''

        sum_of_criteria_values = 0
        for criterium in self.criteria:
            sum_of_criteria_values += self.criteria[criterium]

        for criterium in self.criteria:
            singleton_set = frozenset([criterium])
            self.mu[singleton_set] = self.criteria[criterium]/sum_of_criteria_values

    def set_fm_for_complex_sets(self):
        # set fuzzyMeasure for sets with 2 or more members

        # Random generation of a fuzzy measure mu on a set X
        # note: 'undefined' means we have not yet calculated and stored the value of mu for mu(foo)
        # create list of sets from X and shuffle the list
        list_of_all_subsets = list(self.set_of_all_subsets)
        random.shuffle(list_of_all_subsets)

        for A in list_of_all_subsets:
            if self.mu.get(A) is None:
                minimum_for_mu_A = 0
                maximum_for_mu_A = 1

                subsets_of_A = make_all_subsets(A)

                for B in subsets_of_A:
                    if self.mu.get(B) is not None:
                        minimum_for_mu_A = max(self.mu.get(B), minimum_for_mu_A)

                for B in list_of_all_subsets:
                    if self.mu.get(B) is not None:
                        if B.issuperset(A):
                            maximum_for_mu_A = min(maximum_for_mu_A, self.mu.get(B))

                self.mu[A] = random.uniform(minimum_for_mu_A,maximum_for_mu_A)

class ChoquetIntegral:
    ''' A class to calculate the Choquet Integral given a dictionary of criteria and a related fuzzy measure.

        Inputs
        ------
        The keys in the dictionary of criteria must match the names of the set members used to generate
        the keys to the fuzzy measure values. e.g. the keys in these criteria

            {
                'c1': 0.2,
                'c2': 0.4,
                'c3': 0.1
            }

        could be used to generate the frozensets that are used as the key values to look up values in this dictionary
        of fuzzy measures

            {
                frozenset([]): 0,
                frozenset(['c1']): 0.391304347826087,
                frozenset(['c2']): 0.3478260869565218,
                frozenset(['c3']): 0.2608695652173913,
                frozenset(['c1', 'c2']): 0.7683779330072605,
                frozenset(['c1', 'c3']): 0.8093446720056068,
                frozenset(['c2', 'c3']): 0.41548536225285937,
                frozenset(['c1', 'c2', 'c3']): 1
            }

        Outputs
        ------
        The class returns a single real number that is the Choquet Integral.  This value is the sum of the
        products of the differences between sorted criteria values and the corresponding fuzzy measures.

    '''

    def __init__(self,criteria={}, fuzzyMeasure={}):
        '''instantiate a Choquet Integral object'''
        self.criteria = criteria
        self.mu = fuzzyMeasure

    def get_criteria_keys_sorted_by_value(self):
        '''create the attribute, sigma, a list of criteria sorted by value'''
        self.criteria_keys_sorted_by_value = []

        # sort the criteria by value
        criteria_sorted_by_value = sorted(self.criteria.items(), key=operator.itemgetter(1))

        # make a list of the criteria keys in the
        for criterium in criteria_sorted_by_value:
            self.criteria_keys_sorted_by_value.append(criterium[0])

        return self.criteria_keys_sorted_by_value

    def calculate(self):
        '''Calculate the Choquet Integral and return just that value'''

        # initialize variables for loop
        self.utility=0
        x_n_minus_1 = 0
        self.get_criteria_keys_sorted_by_value()
        my_keys = self.criteria_keys_sorted_by_value[:]
        set_of_criteria = frozenset(my_keys)

        for criterum in self.criteria_keys_sorted_by_value:
            self.utility += (self.criteria[criterum] - x_n_minus_1) * self.mu[set_of_criteria]
            # set up for next loop
            x_n_minus_1 = self.criteria[criterum]
            my_keys.pop(0)
            set_of_criteria = frozenset(my_keys)

        return self.utility

class BestAlternative:
    ''' A class to determine the best alternative given a matrix of labeled alternatives and labeled criteria.

        Input
        -----

        Input data can be in the form of a python dictionary or JSON string with this structure:

            {
                "accuracy": {
                    "fit": 0.1,
                    "sig": 0.2,
                    "col": 0.3
                },
                "comfort": {
                    "fit": 0.4,
                    "sig": 0.5,
                    "col": 0.6
                },
                "duration": {
                    "fit": 0.7,
                    "sig": 0.8,
                    "col": 0.9
                },
                "time": {
                    "fit": 0.4,
                    "sig": 0.3,
                    "col": 0.2
                }
            }

        CSV should also be determined, but that input format is to be determined.

        Output
        ------

        Output should be dict or json string with this structure:

        {
            "best_alternative": "fit",
            "choquet_scores": {
                "fit": 2.8,
                "sig": 1.2,
                "col": 2.0
            },
            "library_version" : "1.0.3",
            ...
        }

        Only "best_alternative" is required.  Other output is optional and expandable.

    '''

    def __init__(self, scores={}, jsonScores='', csvScores=''):
        '''Initialize BestAlternative instance and store input data.
        Input must be the array of responses to N labeled criteria about M labeled alternatives.  '''
        if len(scores) > 0:
            self.setup(json.loads(json.dumps(scores)))
            self.scores=scores
            return(None)
        if len(jsonScores) > 0:
            self.setup(json.loads(jsonScores))
            self.scores=json.loads(jsonScores)
            return(None)
        if len(csvScores) > 0:
            print("error: csv input is not yet supported")
            return(None)
        else:
            print("error: No input supplied")
            return(None)

    def setup(self, jsonScores):
        '''verify the jsonScores is structured correctly'''
        schema = '''
            {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "title": "mdat input",
                "description": "An input data set for the Medical Decision Aids Tool python library",
                "type": "object",
                "patternProperties": {
                    "^.+$": {
                        "$ref": "#definitions/alternatives"
                    }
                },
                "minProperties": 1,
                "definitions": {
                    "alternatives": {
                        "title": "alternative",
                        "description": "an alternative to choose from",
                        "type": "object",
                        "patternProperties": {
                            "^.+$": {
                                "type": "number",
                                "minimum" : 0,
                                "maximum" : 1
                            }
                        },
                        "minProperties": 2
                    }
                }
            }
        '''
        jsonschema.validate(jsonScores, json.loads(schema))

    def get_criteria(self):
        '''return a list containing labels for each criterium'''
        list_of_criteria = self.scores.keys()

    def sum_of_criteria_values(self):
        '''return a dictionary of the sum of each criterium across the alternatives keyed on the criteria labels'''
        dict_of_sums = {}
        for criteria in self.list_of_criteria:
            dict_of_sums[criteria] = sum(float,self.scores[criteria].values())

    def get_alternatives(self):
        '''return a list containing the labels for each alternative'''
        pass

    def get_values_for_an_alternative(self):
        '''return a dictionary of values for a single alternative, keyed on criterium'''
        pass

    def calculate(self):
        # get_criteria from input
        # compute sum_of_criteria_values based on input
        # calculate fuzzyMeasure
        #
        # get_alternatives from input
        # get_values_for_an_alternative from input
        # for alternative in list_of_alternatives:
        #     calculate ChoquetIntegral
        #     store ChoquetIntegral keyed on alternative_label
        #
        # return alternative_label for the highest stored choquetIntegral
        resultJSONString = '''
            {
                "best_alternative": "fit",
                "choquet_scores": {
                    "fit": 2.8,
                    "sig": 1.2,
                    "col": 2.0
                }
            }
        '''
        result = json.loads(resultJSONString)
        return(result)


def main():
    '''
    A class to determine the best alternative given a matrix of labeled alternatives and labeled criteria.

    Input
    -----

    Input data can be in the form of a JSON string with this structure:

        {
            "accuracy": {
                "fit": 0.1,
                "sig": 0.2,
                "col": 0.3
            },
            "comfort": {
                "fit": 0.4,
                "sig": 0.5,
                "col": 0.6
            },
            "duration": {
                "fit": 0.7,
                "sig": 0.8,
                "col": 0.9
            },
            "time": {
                "fit": 0.4,
                "sig": 0.3,
                "col": 0.2
            }
        }


    Output
    ------

    Output data is either a string with the label of the best alternative or a json string in this format

    {
        "best_alternative": "fit",
        "choquet_scores": {
            "fit": 2.8,
            "sig": 1.2,
            "col": 2.0
        }
    }


    Usage:

        usage: mdat.py [-h] [-i {json}] [-o {json,brief}] [infile] [outfile]

        Select the best of two or more alternatives given responses to a list of
        criteria

        positional arguments:
          infile
          outfile

        optional arguments:
          -h, --help            show this help message and exit
          -i {json}, --input {json}
                                Specify the file type used as input. Valid types: json
          -o {json,brief}, --output {json,brief}
                                Specify the file type used as input. Valid types:
                                json, text
    '''

    # define the list of acceptable arguments
    parser = argparse.ArgumentParser(
        description='Select the best of two or more alternatives given responses to a list of criteria')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument(
        '-i',
        '--input',
        choices=['json'],
        dest='input',
        default='json',
        help='Specify the file type used as input. Valid types: json')
    parser.add_argument(
        '-o',
        '--output',
        choices=['json', 'brief'],
        dest='output',
        default='brief',
        help='Specify the file type used as input. Valid types: json, text')

    # prepare the arguments we were given
    args = parser.parse_args()

    # Prepare the input
    if args.input == 'json':
        ba = BestAlternative(jsonScores=args.infile.read())
    else:
        print "Unsupported input type"
        return()

    # generate and return the output
    if args.output == 'json':
        args.outfile.write(json.dumps(ba.calculate()))
    elif args.output == 'brief':
        args.outfile.write(ba.calculate()['best_alternative'])
    else:
        print "Unsupported output type"
        return()


if __name__ == "__main__":
    main()
