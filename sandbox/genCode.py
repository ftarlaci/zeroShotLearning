import random
import json
from tree import *
import numpy as np
import operator
from htmlGenerator import *

NPROGRAMS = 1000000

def main():
	decisionTrees = loadDecisionTrees()
	countMap = {}
	labelMap = {}
	for i in range(NPROGRAMS):
		if i % 10000 == 0: 
			print i, len(countMap)
		decisions = set(collectDecisions(decisionTrees))
		tree = generateCode(decisions)
		code = tree.makeCode()
		codeString = str(code)
		countTree(countMap, labelMap, decisions, codeString)
	generateHtml(countMap, labelMap)

def getLabelProbability(labelMap, treeStr, count):
	decisionCount = {}
	decisions = labelMap[treeStr]
	for decisionSet in decisions:
		for d in decisionSet:
			if not d in decisionCount:
				decisionCount[d] = 0.0
			decisionCount[d] += 1
	for key in decisionCount:
		decisionCount[key] /= count
	return decisionCount

def countTree(countMap, labelMap, decisions, tree):
	decisionStr = getDecisionStr(decisions)
	treeStr = str(tree)
	if not treeStr in countMap:
		countMap[treeStr] = 0
	countMap[treeStr] += 1
	if not treeStr in labelMap:
		labelMap[treeStr] = {}
	if not decisionStr in labelMap[treeStr]:
		labelMap[treeStr][decisionStr] = 0
	labelMap[treeStr][decisionStr] += 1

def getDecisionStr(decisions):
	decisionList = list(decisions)
	decisionList.sort()
	decisionStr = ''
	for d in decisionList:
		decisionStr += d + '\n'
	return decisionStr
	
def loadDecisionTrees():
	trees = []
	treeNames = json.load(open('input/p1/decisions.json'))
	for name in treeNames:
		filePath = 'input/p1/' + name + '.json'
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

########### GENERATE CODE ###############

def generateCode(decisions):
	block = Tree('Block')
	if 'AddColor' in decisions:
		colorBlock = getColorBlock(decisions)
		block.addChild(colorBlock)
	if 'ClockwisePlan' in decisions:
		if 'ClockwiseExtraTurn' in decisions:
			block.addChild(generateFirstTurn(decisions))
		block.addChild(generateRepeat(decisions))
	if 'CounterClockwisePlan' in decisions:
		block.addChild(generateRepeat(decisions))
	if 'NoPlan' in decisions:
		block = generateRandomCode(decisions, 0)
	block.normalize()
	return block

def getColorBlock(decisions):
	block = Tree('Color')
	if 'AddRandomColor' in decisions:
		block.addChild(Tree('Red'))
	else:
		block.addChild(Tree('Random'))
	return block

def generateFirstTurn(decisions):
	left = not 'LeftRightConfusion' in decisions
	angle = 90
	if 'ThinkTriangle' in decisions:
		angle = 60
		if random.random() < 0.5:
			angle = 30

	if 'AngleInvariance' in decisions:
		left = not left
		angle = 360 - angle
 
	code = Tree(getTurnString(left))
	code.addChild(Tree(str(angle)))
	return code

def generateRepeat(decisions):
	if 'GetRepeat' in decisions:
		n = getRepeatN(decisions)
		repeat = Tree('Repeat')
		repeat.addChild(Tree(str(n)))
		repeat.addChild(generateBody(decisions))
		if doesntUnderstandNesting(decisions):
			
			repeatBody = repeat.children[1] # This is a block node
			assert len(repeatBody.children) == 2


			newBlock = Tree('Block')
			newBlock.addChild(repeat)
			newBlock.addChild(repeatBody.children[1])
			repeat.children[1] = repeatBody.children[0]

			return newBlock
		else:
			return repeat
	else:
		code = Tree('Block')
		nBodies = getBodiesN(decisions)
		bodyCode = generateBody(decisions)
		for i in range(nBodies):
			code.addChild(bodyCode)
		return code

def doesntUnderstandNesting(decisions):
	if 'DontGetNesting' in decisions:
		if 'GetBodyCombo' in decisions:
			return True
	return False

def generateBody(decisions):
	if 'GetBodyCombo' in decisions:
		body = Tree('Block')
		if 'GetBodyComboOrder' in decisions:
			body.addChild(generateMove(decisions))
			body.addChild(generateBodyTurn(decisions))
		else:
			body.addChild(generateBodyTurn(decisions))
			body.addChild(generateMove(decisions))
		return body
	if 'OneBlockBody' in decisions:
		if random.random() < 0.5:
			return generateMove(decisions)
		else:
			return generateBodyTurn(decisions)
	if 'BodyConfusion' in decisions:
		return generateRandomCode(decisions, 0)

def generateMove(decisions):
	code = Tree('Move')
	if 'Move50' in decisions:
		code.addChild(Tree(str(50)))
	else:
		code.addChild(Tree(str(100)))
	return code

def getBodiesN(decisions):
	if 'NoRepeat' in decisions:
		return 1
	if 'GetThreeSides' in decisions:
		return 3
	return random.choice([2, 4])

def getRepeatN(decisions):
	if 'GetThreeSides' in decisions:
		return 3
	if 'NoRepeatCounterAttempt' in decisions:
		return 0
	if 'DontGetThreeSides' in decisions:
		return random.choice([1, 2, 4])

def generateBodyTurn(decisions):
	isLeft = 'CounterClockwisePlan' in decisions
	angle = getBodyAngle(decisions)
	if 'LeftRightConfusion' in decisions:
		isLeft = not isLeft
	if 'Angle360Invariance' in decisions:
		isLeft = not isLeft
		angle = 360 - angle
	code = Tree(getTurnString(isLeft))
	code.addChild(Tree(str(angle)))
	return code

def getBodyAngle(decisions):
	if 'ThinkSquare' in decisions:
		return 90
	if 'CounterClockwisePlan' in decisions:
		if 'ThinksToInvertAngle' in decisions:
			return 120
		return 60
	else:
		return 60


def getTurnString(isLeft):
	if isLeft:
		return 'TurnLeft'
	return 'TurnRight'

def generateRandomCode(decisions, depth):
	c = random.random()
	p = 0.8 + depth * 0.1
	if c < p:
		return generateRandomTerminal(decisions, depth)
	else:
		code = Tree('Block')
		code.addChild(generateRandomTerminal(decisions, depth))
		code.addChild(generateRandomCode(decisions, depth+1))
		return code

def generateRandomTerminal(decisions, depth):
	if random.random() < 0.9:
		if random.random() < 0.5:
			code = Tree('Move')
			amount = random.choice([0, 50, 100, 150])
			code.addChild(Tree(str(amount)))
			return code
		else:
			left = random.random()
			angle = random.choice(range(0, 390, 30))
			code = Tree(getTurnString(left))
			code.addChild(Tree(str(angle)))
			return code
	else:
		code = Tree('Repeat')
		n = random.randint(1, 4)
		code.addChild(Tree(str(n)))
		code.addChild(generateRandomCode(decisions, depth+1))
		return code

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