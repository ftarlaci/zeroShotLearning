import operator

def conceptMarginal(codeDecisionMap):
	totalPrograms = 0.0
	labelCountMap = {}
	for label in getImportantLabels():
		labelCountMap[label] = 0
	for codeStr in codeDecisionMap:
		decisionListCountMap = codeDecisionMap[codeStr]
		for decisionStr in decisionListCountMap:
			count = decisionListCountMap[decisionStr]
			decisionSet = set(getDecisionList(decisionStr))
			for d in labelCountMap:
				if d in decisionSet:
					labelCountMap[d] += count
			totalPrograms += count
	marginalP = {}
	for d in labelCountMap:
		marginalP[d] = labelCountMap[d] / totalPrograms
	return marginalP

def getSignificantConcents(marginal, decisionListCountMap, count):
	labelCondCountMap = {}
	for d in marginal:
		labelCondCountMap[d] = 0
	for decisionStr in decisionListCountMap:
		decisionListCount = decisionListCountMap[decisionStr]	
		decisionSet = set(getDecisionList(decisionStr))
		for d in labelCondCountMap:
			if d in decisionSet:
				labelCondCountMap[d] += decisionListCount
	
	condP = {}
	for d in labelCondCountMap:
		condP[d] = labelCondCountMap[d] / (count * 1.0)

	significantList = []
	significanceMap = {}
	for d in getImportantLabels():
		isPlan = False
		if d == 'ClockwisePlan' or d == 'CounterClockwisePlan':
			isPlan = True
		oddYes = condP[d] / marginal[d]
		if oddYes > 1.1 or isPlan:
			significantList.append(d)
			significanceMap[d] = oddYes

	return significantList, significanceMap

def getImportantLabels():
	return [
		'ClockwisePlan',
		'CounterClockwisePlan',
		'NoPlan',
		'NoRepeat',
		'DontGetThreeSides',
		'NoRepeatCounterAttempt',
		'NoClockwiseExtraTurn',
		'MultipleBodies',
		'BodyConfusion',
		'OneBlockBody',
		'DontGetNesting',
		'DontGetBodyComboOrder',
		'MoveDefault',
		'LeftRightConfusion',
		'ThinkSquare',
		'DontInvertAngle'
	]

def getDecisionList(decisionStr):
	newList = []
	for v in decisionStr.split('\n'):
		if v: newList.append(v)
	return newList