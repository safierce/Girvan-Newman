import sys
import json
from pprint import pprint

in_fname  = sys.argv[1] 
out_fname = sys.argv[2]

if __name__ == '__main__':
	 
	with open(in_fname, 'r') as f:
		edges = []
		nodes = []
		for line in f:
			edge = json.loads(line)
			edges.append(tuple(edge))
			for edge in edges:
				for node in edge:
					if node not in nodes:
						nodes.append(node)
			nodes = nodes
	data = {}
	for node in nodes:
    
		data[node] = {0: [node]}
		level = 1
		search = True
		while search:
			search = False
			data[node][level] = []
			current_nodes = data[node][level-1]
			try:
				parent_nodes = data[node][level-2]
			except KeyError:
				parent_nodes = [None]

			for current_node in current_nodes:
				for edge in edges:
					
					if current_node in edge:
						child = edge[1] if current_node == edge[0] else edge[0]
					else:
						continue
					if child in current_nodes + parent_nodes:
						pass
					elif child in data[node][level]:
						pass
					else:
						search = True
						data[node][level].append(child)
			
			if search:
				data[node][level] = sorted(data[node][level])
				level += 1
			else:
				if not bool(data[node][level]):
					del data[node][level]

		# determine number of levels (including root)
		data[node]['nlevels'] = len(data[node])

	for node, sd in data.items():
    
		sd['nodes'] = nodes
		for node in nodes:
			sd[node] = {"parents": [],"children": [],"label": None,"level": None,"credit": None,"leaf": False}

		for level in range(sd['nlevels']):
			if level == 0:
				node = sd[0][0]
				if sd['nlevels'] > 1:
					sd[node]['children'] = sd[1]
				sd[node]['level'] = level
				sd[node]['label'] = 1
			else:
				for node in sd[level]:
				
					conns = []
					for edge in edges:
						if node in edge and edge not in conns:
							conns.append(edge)
					for edge in conns:
						nd = edge[1] if node == edge[0] else edge[0]
                    
						if nd in sd[level-1]:
							sd[node]['parents'].append(nd)
						elif nd in sd[level]:
							pass
						else:
							sd[node]['children'].append(nd)
					sd[node]['level'] = level
					sd[node]['label'] = len(sd[node]['parents'])
	
	for node, sd in data.items():
		
		sd['edges'] = edges
		for edge in edges:
			edge_s="(" + edge[0] + ", " + edge[1] + ")"
			sd[edge_s] = {'sum': None}
    
		for level in range(sd['nlevels']-1, 0, -1):
			for node in sd[level]:
				
				sd[node]['leaf'] = not bool(sd[node]['children'])	
				sd[node]['sum'] = 1.0

				for child in sd[node]['children']:
					edge = tuple(sorted([node, child]))
					edge_key = "(" + edge[0] + ", " + edge[1] + ")"
					sd[node]['sum'] += float(sd[edge_key]['sum'])
            
				label_tot = float(sum([sd[par]['label'] for par in sd[node]['parents']]))
				for parent in sd[node]['parents']:
					edge = tuple(sorted([node, parent]))
					edge_key = "(" + edge[0] + ", " + edge[1] + ")"
					sd[edge_key]['sum'] = float(sd[node]['sum']) * (float(sd[parent]['label'])/label_tot)
	
	betweenness = {}
	for edge in edges:
		edge_key = "(" + edge[0] + ", " + edge[1] + ")"
		vals = [data[node][edge_key]['sum'] for node in nodes]
		if None in vals:
			vals2 = [v for v in vals if v is not None]
			vals = vals2
		betweenness[edge_key] = sum(vals) / 2.0

	with open(out_fname, 'w') as f:
		for edge in edges:
			edge_key = "(" + edge[0] + ", " + edge[1] + ")"
			value = betweenness[edge_key]
			f.write(edge_key + ", {:.1f}\n".format(value))