#!/usr/bin/env python

import operator
from plugins.bottle.bottle import SimpleTemplate
import numpy as np
from conceptStats import *

MAX_TO_SHOW = 500

html = open('output/p1/treeTable.html', 'w')

def generateHtml(countMap, codeDecisionMap):
	global html
	html.write('<div class="table-responsive">\n')
	html.write('<table class="table">\n')
	html.write('<thead><tr><th>#</th><th>Code</th><th>Labels</th><th>Most Common</th><th>Odds</th></tr></thead>\n')
	html.write('<tbody>\n')

	marginal = conceptMarginal(codeDecisionMap)

	sortedTrees = sorted(countMap.items(), key=operator.itemgetter(1), reverse=True)
	for i in range(len(sortedTrees)):
		treeStr = sortedTrees[i][0]
		count = sortedTrees[i][1]
		labelCountMap = codeDecisionMap[treeStr]
		rowHtml(treeStr, count, labelCountMap, marginal)
		if i >= MAX_TO_SHOW: break

	html.write('</tbody>\n')
	html.write('</table>\n')
	html.write('</div>')
	html.close()

	with open('output/p1/treeResults.html', 'w') as resultsFile:
		with open('output/p1/treeTemplate.html') as templateFile:
			templateText = templateFile.read()
			compiledHtml = SimpleTemplate(templateText).render()
			resultsFile.write(compiledHtml)

def rowHtml(treeStr, count, labelCountMap, marginal):
	global html
	html.write('<tr>\n')
	html.write('<td>' +str(count)+ '</td>\n')
	html.write('<td><pre>' +treeStr+ '</pre>\n')
	
	labels, odds = getSignificantConcents(marginal, labelCountMap, count)

	sigLabelCountMap = getSignificantLabelCountMap(labelCountMap, labels)
	mostCommonLabels = sorted(sigLabelCountMap.items(), key=operator.itemgetter(1), reverse=True)
	n = min(3, len(mostCommonLabels))
	m = len(labels)

	# Calculate labelBools
	labelBools = np.zeros((m, n))
	for c in range(n):
		decisionStr = mostCommonLabels[c][0]
		decisionCount = mostCommonLabels[c][1]
		decisions = set(decisionStr.split('\n'))
		for r in range(m):
			if labels[r] in decisions:
				labelBools[r][c] = 1

	# Label Table
	html.write('<td>\n')
	html.write('<div class="table-responsive">\n')
	html.write('<table class="table table-condensed">\n')
	html.write('<tbody>\n')
	for r in range(m):
		html.write('<tr>\n')
		html.write('<td>'+labels[r]+'</td>\n')
		html.write('</tr>\n')
	html.write('</tbody>\n')
	html.write('</table>\n')
	html.write('</div>\n')
	html.write('</td>\n')

	# Most Common Table
	html.write('<td>\n')
	html.write('<div class="table-responsive">\n')
	html.write('<table class="table table-condensed" style="text-align:center">\n')
	html.write('<tbody>\n')
	for r in range(m):
		html.write('<tr>')
		for c in range(n):
			labelBool = labelBools[r][c] == 1
			labelClass = "success"
			if not labelBool: labelClass = "danger"
			html.write('<td class="'+labelClass+'">'+str(labelBool)+'</td>\n')
		html.write('</tr>')
	# Count Row	
	html.write('<tr>\n')
	for c in range(n):
		decisionCount = mostCommonLabels[c][1]
		pct = 100.0 * decisionCount / count
		html.write('<td>%.1f%%</td>' % round(pct,1) + '</td>')
	html.write('</tr>\n')

	html.write('</tbody>\n')
	html.write('</table>\n')
	html.write('</div>')

	html.write('</td>\n')

	# Show the odds
	html.write('<td>\n')
	html.write('<div class="table-responsive">\n')
	html.write('<table class="table table-condensed" style="width:400px !important">\n')
	#html.write('<thead><tr><th style="width:100px">Odds</th><th></th></tr></thead>\n')
	for l in labels:
		oddRatio = odds[l]
		html.write('<tr>')
		html.write('<td style="width:100px">%.2f</td>' % round(oddRatio,2))
		html.write('<td>')
		html.write(getProgressBar(oddRatio / 10.0))
		html.write('</td>')
		html.write('</tr>')
	html.write('</table>\n')
	html.write('</div>')
	html.write('</td>\n')

	html.write('</tr>\n')

def getProgressBar(pct):
	v = pct * 100
	pBar = ''
	pBar += '<div class="progress" style="margin-bottom:0 !important">'
	pBar += '<div class="progress-bar" role="progressbar" aria-valuenow="'+str(v)+'" aria-valuemin="0" aria-valuemax="100" style="width: '+str(v)+'%;">'
	pBar += '</div>'
	pBar += '</div>'
	return pBar

def getSignificantLabelCountMap(labelCountMap, labels):
	sigLabelCountMap = {}
	sigLabelSet = set(labels)
	for labelListStr in labelCountMap:
		count = labelCountMap[labelListStr]
		labelList = getDecisionList(labelListStr)
		newList = []
		for d in labelList:
			if d in sigLabelSet:
				newList.append(d)
		newListStr = getDecisionStr(newList)
		if not newListStr in sigLabelCountMap:
			sigLabelCountMap[newListStr] = 0
		sigLabelCountMap[newListStr] += count
	return sigLabelCountMap

def getDecisionStr(decisions):
	decisionList = list(decisions)
	decisionList.sort()
	decisionStr = ''
	for d in decisionList:
		decisionStr += d + '\n'
	return decisionStr

def getAllLabels(labelCountMap):
	mistakes = [
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
	allLabelsSeen = set([])
	for labels in labelCountMap:
		lines = labels.split('\n')
		for line in lines:
			if line:
				if line in mistakes:
					allLabelsSeen.add(line)
	finalList = []
	for m in mistakes:
		if m in allLabelsSeen:
			finalList.append(m)
	return finalList

		