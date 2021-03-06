import numpy as np
import scipy as sp
import pickle
from scipy.stats import beta

class PBM_TS:
	def __init__(self, itemid, posProb):
		self.K = len(itemid)
		self.L = len(posProb)
		self.turn = 0 # how many times selected item list
		self.itemid = itemid
		self.posProb = posProb
		self.S = [[1 for _ in range(self.L)] for __ in range(self.K)]
		self.N = [[2 for _ in range(self.L)] for __ in range(self.K)]
		self.Nc = [[2.0 for _ in range(self.L)] for __ in range(self.K)]
		#self.expect = [0.0 for _ in range(self.L)] # arm expectation

	def rejection_sampling(self, k, m):
		step = 0.01
		x = step + 0.0; M_cand = []
		while x <= 1:
			M_cand.append(self.target_pdf(x, k))
			x += step
		'''M_cand = []
		for i in range(100):
			M_cand.append(self.target_pdf(np.random.uniform(low=0,high=0.999)+0.0005, k))'''
		logM = max(M_cand)
		cnt = 0
		for i in range(100):
			cnt += 1
			z0 = self.sample_proposal_distribution(k, m)
			uni = np.random.uniform(low=0, high=self.proposal_pdf(z0, k, m))
			if logM + np.log(uni) <= self.target_pdf(z0, k):
				return z0
		return 0
		

	#return log(val) because val is too small
	def target_pdf(self, x, k):
		return sum([(np.log(x) * self.S[k][l]) + (np.log(1 - self.posProb[l] * x) * (self.N[k][l]-self.S[k][l]))
			for l in range(self.L)])
			

	def sample_proposal_distribution(self, k, m):
		return np.random.beta(self.S[k][m], self.N[k][m] - self.S[k][m]) / self.posProb[m]
		#return np.random.uniform(0, 1)

	def proposal_pdf(self, x, k, m):
		return beta.pdf(x, self.S[k][m], self.N[k][m] - self.S[k][m])
		#return 1

	#return sorted list of item numbers, with length require_num
	def select_items(self, required_num):
		self.turn += 1
		sample_val = [0.0] * self.K
		for k in range(self.K):
			m = np.argmax(self.N[k])
			#print('arm %d/%d' % (k, self.K))
			z0 = self.rejection_sampling(k, m)
			#z0 = self.sample_proposal_distribution(k, m)
			sample_val[k] = z0
		items = sorted([(sample_val[k], k) for k in range(self.K)], reverse=True)
		result = [items[i][1] for i in range(required_num)]
		return result


	def update(self, selected_items, feedback):
		assert len(selected_items) == len(feedback)
		for l in range(len(selected_items)):
			k = selected_items[l]
			self.N[k][l] += 1
			self.Nc[k][l] += self.posProb[l]
			if feedback[l]:
				self.S[k][l] += 1
	
	def save(self, fname):
		with open(fname, 'wb') as f:
			pickle.dump(self, f)

	def load(self, fname):
		with open(fname, 'rb') as f:
			sim = pickle.load(f)
			self.K = sim.K
			self.L = sim.L
			self.turn = sim.turn
			self.itemid = sim.itemid
			self.posProb = sim.posProb
			self.S = sim.S
			self.N = sim.N
			self.Nc = sim.Nc