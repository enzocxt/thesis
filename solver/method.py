import os, sys, time
import platform
import subprocess
import utils
from Pattern import *

# ----------------------------------------------------------
# gSpan command:
# ./gSpan -file [file_name] -support [support: float] &> log

# prefixSpan command:
# ./exec/cpsm [options] [[dataset] [minimum frequency threshold]]

# eclat command:
# ./eclat [options] infile [outfile]
# ./eclat -s10 ./output/eclat/zoo-1.txt
# ----------------------------------------------------------

class Mining(object):
    """Abstract class"""

    def __init__(self, inputs):
        # example: inputs{'type': 'itemset', 'matching': 'exact', 'constraints': 'frequency', 'dominance': 'max'}
        #self.inputs = inputs
        self.type = inputs['type']
        if 'matching' in inputs:
            self.matching = inputs['matching']
        else:
            self.matching = None
        if 'constraint' in inputs:
            self.constraint = inputs['constraint']
        else:
            self.constraint = None
        if 'dominance' in inputs:
            self.dominance = inputs['dominance']
        else:
            self.dominance = None
        if 'support' in inputs:
            self.support = float(inputs['support'])
        else:
            self.support = 0.1
        if 'datafile' in inputs:
            self.datafile = os.getcwd() + '/' + inputs['datafile']
            #self.datafile = inputs['datafile']
        else:
            print 'Need input data file!'
            sys.exit(2)
        if 'output' in inputs:
            self.output = os.getcwd() + '/' + inputs['output']
        else:
        #    print 'Need specify output file!'
        #    sys.exit(2)
            self.output = "-"
        self.patternSet = None

    def mining(self):
        pass

    def parser(self):
        pass


class gSpan(Mining):
    """Use gSpan to mining frequent subgraphs"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        if platform.system() == "Linux":
            gSpan = "/home/enzo/Thesis/MAI-Thesis/exec/gspan"
        else:
            gSpan = "gspan"
        options = ''
        if self.support:
            options = ''.join('-support %s' % self.support)

        #print("%s -file %s %s" % (gSpan, self.datafile, options))
        print([gSpan, "-file", self.datafile, options])
        child = subprocess.Popen([gSpan, "-file", self.datafile, options, "&> ", self.output], shell=False, stdout=subprocess.PIPE)
        try:
            output = subprocess.check_output([gSpan, "-file", self.datafile, options])
            returncode = 0
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode
        print(output)
        print(returncode)

        #result = child.stdout.read()
        result = child.communicate()[0]
        print result
        #self.parser(result)
        #fout = open(self.output, 'w')
        #fout.write(result)
        #fout.close()
        return result

    def parser(self, stdOutput, path=None):
        self.patternSet = self.parserGraph(stdOutput)
        #self.patternSet = utils.parser(self, stdOutput)
        #self.patternSet = utils.parser(self, None, self.output)
        return self.patternSet

    def parserGraph(self, stdOutput, path=None):
        if not path:
            lines = stdOutput.split('\n')
        else:
            fg = open(path, 'r')
            lines = fg.readlines()
            fg.close()
        graphs = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if 't #' in line:  # t # 0 * 45
                t = line.split(' ')
                graph = Graph(t[4])
                graph.id = t[2]
                i += 1
                while i < len(lines):
                    line = lines[i]
                    if 'v ' in line:
                        v = line.split(' ')  # v 0 2
                        node = Node()
                        node.id = v[1]
                        node.label = v[2]
                        graph.add_node(node)
                        i += 1
                    elif 'e ' in line:
                        e = line.split(' ')  # e 0 1 0
                        edge = Edge()
                        edge.fromnode = e[1]
                        edge.tonode = e[2]
                        edge.label = e[3]
                        graph.add_edge(edge)
                        i += 1
                    else:
                        break
                graphs.append(graph)
                if i < len(lines) and 't #' not in lines[i]:
                    i += 1
                elif i < len(lines) and 't #' in lines[i]:
                    continue
            else:
                i += 1

        return graphs

    def getPatterns(self):
        return self.patternSet


class prefixSpan(Mining):
    """Use prefixSpan to mining frequent sequences"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        if platform.system() == "Linux":
            prefixSpan = "./exec/cpsm"
        else:
            prefixSpan = "prefixSpan"
        options = ''

        child = subprocess.Popen([prefixSpan, options, self.datafile, str(self.support)], stdout=subprocess.PIPE)
        result = child.communicate()[0]
        return result

    def parser(self, stdOutput, path=None):
        #self.patternSet = utils.parser(self, stdOutput)
        self.patternSet = self.parserSequence(stdOutput)
        return self.patternSet

    def parserSequence(self, stdOutput, path):
        """
            If path == "" or path == None,
            means that do not write results into a file
        """
        patterns = []
        if path == "" or not path:
            output = stdOutput.split('\n')
            for line in output:
                if 'Pattern' in line:
                    patterns.append(line.split()[2:])
        else:
            with open(path, 'r') as fin:
                for line in fin:
                    if 'Pattern' in line:
                        patterns.append(line.split()[2:])

        return patterns

    def getPatterns(self):
        return self.patternSet


class prefixSpan_py(Mining):
    """python version of prefixSpan"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        S = utils.read_csv(self.datafile)
        self.patternSet = utils.prefixSpan(S, Sequence([], sys.maxint), self.support)

    def getPatterns(self):
        return self.patternSet

    def print_patterns(self):
        utils.print_patterns(self.patternSet)


class eclat(Mining):
    """Use eclat to mining frequent itemsets"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)
        self.eclat_exec = None

    def mining(self):
        """Mining frequent itemsets by (closed) eclat"""
        if platform.system() == "Linux":
            self.eclat_exec = "./exec/eclat"
        else:
            self.eclat_exec = "eclat"

        # add options of eclat
        options = ''
        if self.support:
            options += '-s%s' % int(self.support*100)
        if self.dominance == 'max':
            options += 'tm'
        elif self.dominance == 'closed':
            options += 'tc'
        # output absolute item set support
        options += 'v (%a)'

        #child = subprocess.Popen([self.eclat_exec, options, self.datafile, self.output], stdout=subprocess.PIPE)
        child = subprocess.Popen([self.eclat_exec, options, self.datafile, "-"], stdout=subprocess.PIPE)

        stdOutput = child.stdout.read()
        if self.output == "" or self.output == "-":
            fout = open("output/closed_eclat.txt", 'w')
            fout.write(stdOutput)
            fout.close()
            #self.patternSet = utils.parser(self, result, "output/closed_eclat.txt")
            #self.patternSet = utils.parser(self, result, "-")
        return stdOutput

    def closedMining(self):
        """
        if mining closed frequent itemsets
        use eclat to find frequent itemset
        and use python post-process to find closed itemsets
        """
        if platform.system() == "Linux":
            eclat = "./exec/eclat"
        else:
            eclat = "eclat"

        child = subprocess.Popen([eclat, "-s%s" % self.support, self.datafile, ""], stdout=subprocess.PIPE)
        result = child.stdout.read()
        if self.dominance == 'max':
            self.maxParser(result)
        elif self.dominance == 'closed':
            closedPatterns = self.closedParser(result)
            return closedPatterns

    def parser(self, stdOutput, path=None):
        self.patternSet = self.parserItemset(stdOutput)
        #self.patternSet = utils.parser(self, None, "output/closed_eclat.txt")
        return self.patternSet

    def parserItemset(self, stdOutput, path=None):
        """
            If path == "" or path == "-",
            means that do not write results into a file
        """
        if not path or path == "" or path == "-":
            result = stdOutput.split('\n')
        else:
            fin = open(path, 'r')
            result = fin.readlines()
            fin.close()
        itemsets = []
        for i, line in enumerate(result):
            line.strip()
            items = line.split(' ')
            if not items[0].isdigit():
                continue
            if '(' in items[-1]:
                support = items.pop().strip()
                # e.g.: 22 32 20 (46)
                support = int(support[1:-1])
                itemset = Itemset(i+1, items, support)
                itemsets.append(itemset)

        return itemsets

    def maxParser(self, stdOutput):
        """For maximal item sets"""
        pass

    def closedParser(self, stdOutput):
        """
        For closed item sets
        Directly check closed itemsets
        Do not store them into python objects,
        and not use objects.method to check closed
        """
        #closedParserTime0 = time.time()
        # itemsets: a dictionary of itemset list
        # itemsets of the same list have same support
        itemsets = {}
        stdOutput = stdOutput.split('\n')
        # pass the description lines
        tmp = stdOutput.pop()
        tmpList = tmp.split()
        while not tmpList[0].isdigit():
            tmp = stdOutput.pop()
            tmpList = tmp.split(' ')
        stdOutput.append(tmp)

        for line in stdOutput:
            line.strip('\n')
            items = line.split(' ')
            support = items.pop()
            support = float(support[1:-1])
            itemset = (support, set(items))

            # if itemsets dictionary has support of this itemset
            # add this itemset to that list
            # else add this itemset as a new itemset list
            if itemsets.has_key(itemset[0]):
                itemsets[itemset[0]].append(itemset[1])
            else:
                itemsets[itemset[0]] = [itemset[1]]

        def checkClosed(itemset, itemsetList):
            for it in itemsetList:
                if len(itemset) >= len(it):
                    continue
                elif itemset < it:
                    return False
            return True

        # find closed itemset
        closedItemset = []
        for list in itemsets.values():
            for i in range(len(list)):
                if checkClosed(list[i], list):
                    closedItemset.append(list[i])

        return closedItemset

    def getPatterns(self):
        return self.patternSet
