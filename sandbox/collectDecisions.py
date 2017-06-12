import random
import json
from tree import *
import numpy as np
import operator

def main():
	decisionSet = set([])
	decisionTrees = loadDecisionTrees()
	for i in range(10000):
		decisions = set(collectDecisions(decisionTrees))
		decisionSet.update(decisions)
	for decision in decisionSet:
		print decision
	
def loadDecisionTrees():
	trees = []
	treeNames = json.load(open('p1/decisions.json'))
	for name in treeNames:
		filePath = 'p1/' + name + '.json'
		tree = json.load(open(filePath))
		trees.append(tree)
	return trees

def collectDecisions(decisionTrees):
	decisions = []
	for tree in decisionTrees:
		decisions.extend(chose(tree))
		if 'NoPlan' in decisions: 
			return decisions
	return decisions

########## MAKE DECISIONS ###############

def chose(decisionTree):
	d = []

	# Base Case
	if not 'children' in decisionTree: 
		return []

	# Recursive Case
	children = decisionTree['children']
	child = choseChild(children)
	d.append(child['name'])
	d.extend(chose(child))
	return d


def choseChild(children):
	weights = []
	for child in children:
		weights.append(float(child['weight']))
	p = np.array(weights) / sum(weights)
	return np.random.choice(children, p=p)



if __name__ == '__main__':
	main()