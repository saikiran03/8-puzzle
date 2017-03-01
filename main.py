import sys
import math
import time
import random
import resource
from collections import Counter
from heapq import heappush, heappop

complementary_move = {
	'U' : 'D',
	'D' : 'U',
	'L' : 'R',
	'R' : 'L'
}
solution_move = {
	'U' : 'Down',
	'D' : 'Up',
	'L' : 'Right',
	'R' : 'Left'
}

class puzzle:

	def __init__(self, state, parent=0):
		self.state = state[:]
		self.parent = parent
		self.size = int(math.sqrt(len(state)))
		self.free = state.index(0)
		self.path = []
		return

	def terminal_test(self):
		return (self.state==range(len(self.state)))

	def heuristic(self):
		# manhattan distance
		def ManDist(f):
			v = self.state[f]
			return abs(f/self.size - v/self.size) + abs(f%self.size - v%self.size)

		return sum([ManDist(f) for f in xrange(len(self.state))])

	def actions(self):
		moves = []
		r, c = self.free/self.size , self.free%self.size

		if r!=0:
			moves.append("D")
		if r!=self.size-1:
			moves.append("U")
		if c!=0:
			moves.append("R")
		if c!=self.size-1:
			moves.append("L")

		if (self.parent!=0) and (complementary_move[self.parent] in moves):
			moves.remove(complementary_move[self.parent])

		return moves

	def result(self, move):
		ng = puzzle(self.state, move)
		ng.path = self.path + [move]

		ns = {
			"D" : -ng.size,
			"U" : +ng.size,
			"L" : +1,
			"R" : -1
		}
		ng.state[ng.free] = ng.state[ng.free + ns[move]]
		ng.state[ng.free + ns[move]] = 0
		ng.free = ng.free + ns[move]

		return ng

	def __repr__(self):
		f = ""
		for r in xrange(self.size):
			t = map(str, self.state[r*self.size: (r+1)*self.size])
			f += " ".join(t) + '\n'
		return f


def DLS(board, limit, hf):
	c = Counter()
	stack = [board]

	c['max_fringe_size'] = 0
	while len(stack)>0:
		c['max_fringe_size'] = max(c['max_fringe_size'], len(stack))
		f = stack[-1]
		stack.pop()

		if f.terminal_test():
			c['path_to_goal'] = [solution_move[x] for x in f.path]
			c['cost_of_path'] = len(f.path)
			c['fringe_size'] = len(stack)
			c['search_depth'] = len(f.path)
			return c

		c['nodes_expanded'] += 1
		if hf(f) < limit:
			for act in f.actions()[::-1]:
				stack.append(f.result(act))
				c['max_search_depth'] = max(c['max_search_depth'],len(f.path)+1)

	return None


def dfs(board):
	def helper(node):
		return len(node.path)

	c = Counter()
	dfs_depth_limit = 1
	while True:
		c = DLS(board, dfs_depth_limit, helper)
		if not (c==None):
			break
		dfs_depth_limit += 1

	return c


def ida(board):
	def helper(node):
		return len(node.path) + node.heuristic()

	c = Counter()
	ida_depth_limit = 1
	while True:
		c = DLS(board, ida_depth_limit, helper)
		if not(c==None):
			break
		ida_depth_limit += 1

	return c


def bfs(board):
	c = Counter()
	queue = [board]

	c['max_fringe_size'] = 0
	while len(queue)>0:
		c['max_fringe_size'] = max(c['max_fringe_size'], len(queue))
		f = queue[0]
		queue.pop(0)

		if f.terminal_test():
			c['path_to_goal'] = [solution_move[x] for x in f.path]
			c['cost_of_path'] = len(f.path)
			c['fringe_size']  = len(queue)
			c['search_depth'] = c['cost_of_path']
			return c

		c['nodes_expanded'] += 1
		for act in f.actions():
			queue.append(f.result(act))
			c['max_search_depth'] = len(f.path) + 1


def ast(board):
	c = Counter()
	pQueue = [[board.heuristic(), board]]

	c['max_fringe_size'] = 0
	while len(pQueue) >0:
		c['max_fringe_size'] = max(c['max_fringe_size'], len(pQueue))
		f = heappop(pQueue)

		if f[1].terminal_test():
			c['path_to_goal'] = [solution_move[x] for x in f[1].path]
			c['cost_of_path'] = len(f[1].path)
			c['fringe_size']  = len(pQueue)
			c['search_depth'] = c['cost_of_path']
			return c

		c['nodes_expanded'] += 1
		for act in f[1].actions():
			ns = f[1].result(act)
			heappush(pQueue, [len(ns.path) + ns.heuristic(), ns])
			c['max_search_depth'] = max(c['max_search_depth'], len(f[1].path)+1)

	c['path_to_goal'] = [solution_move[x] for x in solution_path]
	return c


def randomize(shuffles, puzzle):
	for _ in xrange(shuffles):
		moves = puzzle.actions()
		f = int(random.randint(0,len(moves)-1))
		puzzle = puzzle.result(moves[f])

	print "GENERATED PATH:", puzzle.path
	print "EXPECTED PATH :", [complementary_move[x] for x in puzzle.path[::-1]]
	return puzzle

def main():

	method = sys.argv[1]
	istate = sys.argv[2]
	istate = list(map(int, istate.split(',')))
	iboard = puzzle(istate)

	it = time.clock()
	result = eval(method + "(iboard)")

	usage_params = resource.getrusage(resource.RUSAGE_SELF)
	ReqParams = [
	"path_to_goal", "cost_of_path", "nodes_expanded", "fringe_size",
	"max_fringe_size", "search_depth", "max_search_depth", "running_time", "max_ram_usage"
	]
	result["running_time"] = time.clock() - it
	result["max_ram_usage"] = usage_params.ru_maxrss/1024.0

	with open("output.txt", "w") as f:
		for key in ReqParams:
			f.write("%s: %s\n" % (key, result[key]))

if __name__=='__main__':
	main()
