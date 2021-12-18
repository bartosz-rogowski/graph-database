from mysite import db
import pandas as pd
from numpy import isnan
import networkx as nx
from matplotlib.pyplot import figure
from datetime import date
from flask import Response

def delete_all():
	db.run("MATCH (n) DETACH DELETE n")
	

def delete(person):
	p_ID = find_person(person)
	if not p_ID is None:
		db.run("MATCH (n) WHERE ID(n) = $p_ID DETACH DELETE n", p_ID=p_ID)
	

def add_person(fname, lname, born, died=float('NaN')):
	if fname and lname and born:
		db.run("CREATE (p: Person {fname: $fname, lname: $lname, born: $born, died: $died}) RETURN p",
			fname = fname,
			lname = lname,
			born = born,
			died = died
		)
	
	
def add_mock_data():
	people = [
		{"fname": "Lucjan", "lname": "Mostowiak", "born": 1937, "died": 2018},
		{"fname": "Barbara", "lname": "Wrzodak", "born": 1940},
		{"fname": "Maria", "lname": "Mostowiak", "born": 1960},
		{"fname": "Marta", "lname": "Mostowiak", "born": 1972},
		{"fname": "Marek", "lname": "Mostowiak", "born": 1978},
		{"fname": "Małgorzata", "lname": "Mostowiak", "born": 1980},
		{"fname": "Krzysztof", "lname": "Zduński", "born": 1953, "died": 2005},
		{"fname": "Piotr", "lname": "Zduński", "born": 1984},
		{"fname": "Paweł", "lname": "Zduński", "born": 1984},
		{"fname": "Artur", "lname": "Rogowski", "born": 1969},
		{"fname": "Kinga", "lname": "Filarska", "born": 1984},
		{"fname": "Hanna", "lname": "Wasiliak", "born": 1975, "died": 2011},
		{"fname": "Magdalena", "lname": "Zduńska", "born": 2008}
	]
	
	for person in people:
		add_person(
			*tuple( person.values() )
		)
		
	
	add_relationship(people[0], people[1], "MARRIED", {"since": 1959})
	add_relationship(people[4], people[11], "MARRIED", {"since": 2001})
	add_relationship(people[2], people[6], "MARRIED", {"since": 1980})
	add_relationship(people[2], people[9], "MARRIED", {"since": 2011})
	add_relationship(people[7], people[10], "MARRIED", {"since": 2009})
	
	add_relationship(people[0], people[4], "HAS_SON")
	add_relationship(people[1], people[4], "HAS_SON")
	
	add_relationship(people[2], people[7], "HAS_SON")
	add_relationship(people[6], people[7], "HAS_SON")
	
	add_relationship(people[2], people[8], "HAS_SON")
	add_relationship(people[6], people[8], "HAS_SON")
	
	add_relationship(people[0], people[2], "HAS_DAUGHTER")
	add_relationship(people[1], people[2], "HAS_DAUGHTER")
	
	add_relationship(people[0], people[3], "HAS_DAUGHTER")
	add_relationship(people[1], people[3], "HAS_DAUGHTER")
	
	add_relationship(people[0], people[5], "HAS_DAUGHTER")
	add_relationship(people[1], people[5], "HAS_DAUGHTER")

	add_relationship(people[7], people[12], "HAS_DAUGHTER")
	add_relationship(people[10], people[12], "HAS_DAUGHTER")
		
def get_dataframe_with_nodes():
	result = db.run("MATCH (n) RETURN n").data()
	df = pd.DataFrame([ t['n'] for t in result])
	df = df.reindex(columns=['fname', 'lname', 'born', 'died'])
	df.died = df.died.astype('Int64')
	df.fillna(-1, inplace=True)
	df = df.sort_values(by=['born'])
	df = df.reset_index(drop=True)
	return df
	
def get_dataframe_with_relationships():
	query = """
	MATCH (a:Person)-[r]->(b)
	RETURN a, type(r) as type, properties(r) as properties, b
	"""
	result = db.run(query).data()
	df = pd.DataFrame([ t for t in result ])
	return df
	
def plot_graph():
	df = get_dataframe_with_nodes()
	G = nx.DiGraph()
	current_year = date.today().year
	for i in range(len(df)):
		if df.loc[i].died != -1:
			label = df.loc[i].fname + '\n' + df.loc[i].lname + '\ndied in: ' + str(df.loc[i].died) + \
					', aged: ' + str(df.loc[i].died - df.loc[i].born)
		else:
			label = df.loc[i].fname + '\n' + df.loc[i].lname + '\nage: ' + str(current_year - df.loc[i].born)
		G.add_node(label)
		
	df = get_dataframe_with_relationships()
	for i in range(len(df)):
		labels = []
		for person in ['a', 'b']:
			if not isnan(df[person][i]['died']):
				labels.append(
					df[person][i]['fname'] + '\n' + df[person][i]['lname'] + '\ndied in: ' + \
						str(df[person][i]['died']) + ', aged: ' + \
						str(df[person][i]['died'] - df[person][i]['born'])
				)
			else:
				 labels.append(
					  df[person][i]['fname'] + '\n' + df[person][i]['lname'] + '\nage: ' + \
					 str(current_year - df[person][i]['born'])
				 )
		if df['properties'][i]:
			G.add_edge(labels[0],
					   labels[1],
					   reltype = df['type'][i] + '\n' + str(df['properties'][i]) \
						   .replace('{', '').replace('}', '').replace('\'', ''),
					  )
		else:
			 G.add_edge(labels[0],
					   labels[1],
					   reltype = df['type'][i],
					  )

	fig = figure(figsize=(11, 10))
	pos = nx.shell_layout(G, scale = 2)
	nx.draw(G, pos, with_labels=True)
	labels = nx.get_edge_attributes(G, 'reltype')
	nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
	fig.patch.set_alpha(0.15)
	return fig

def find_person(person):
	query = "MATCH (n:Person {fname: $fname, lname: $lname, born: $born}) RETURN ID(n)"
	ID = db.run(query, 
		fname = person["fname"],
		lname = person["lname"],
		born  = person["born"]
	).data()
	if len(ID) == 1:
		return ID[0]["ID(n)"]
	else:
		print("Such person does not exist.")
		return None
	
def add_relationship(person1, person2, reltype, attr=None):
	if person1 != person2:
		if reltype in ["MARRIED", "HAS_SON", "HAS_DAUGHTER", "HAS_CHILD"]:
			query = "MATCH (n:Person {fname: $fname, lname: $lname, born: $born}) RETURN ID(n)"
			p1_ID = find_person(person1)
			p2_ID = find_person(person2)

			if not p1_ID is None and not p2_ID is None:
			
				if reltype == "MARRIED" and attr['since']:
					query = """
						MATCH
						  (p1:Person),
						  (p2:Person)
						WHERE ID(p1) = $p1_ID AND ID(p2) = $p2_ID
						MERGE (p1)-[r:MARRIED {since: $since}]->(p2)
						RETURN type(r)
					"""
					return db.run(query,
								  p1_ID = p1_ID,
								  p2_ID = p2_ID,
								  since = attr['since']
								 ).data()
				else:
					query = f"""
						MATCH
						  (p1:Person),
						  (p2:Person)
						WHERE ID(p1) = $p1_ID AND ID(p2) = $p2_ID
						MERGE (p1)-[r:{reltype}]->(p2)
						RETURN type(r)
					"""
					return db.run(query,
								  p1_ID = p1_ID,
								  p2_ID = p2_ID,
								 ).data()
			else:
				return "ERROR: Same person"
		else: 
			return "No such people in database"
	else: 
		return "Such relationship does not exist"
	
def find_connections(person1, person2):
	p1_ID = find_person(person1)
	p2_ID = find_person(person2)

	if not p1_ID is None and not p2_ID is None:
		query = """
			MATCH path = shortestPath( (p1:Person)-[r*]-(p2:Person) )
			WHERE ID(p1) = $p1_ID AND ID(p2) = $p2_ID
			RETURN path
		"""
		result = db.run(query, p1_ID=p1_ID, p2_ID=p2_ID).data()
		result_list = []
		if not result:
			return None
		for r in result[0]['path'].relationships:
			result_list.append(
				(f"{r.nodes[0]['fname']} {r.nodes[0]['lname']}", 
				type(r).__name__, 
				f"{r.nodes[1]['fname']} {r.nodes[1]['lname']}")
			)
		return result_list

def get_parents(person):
	p_ID = find_person(person)
	if not p_ID is None:
		query = """
			MATCH (p1:Person)<-[:HAS_SON | :HAS_DAUGHTER]-(p2:Person)
			WHERE ID(p1) = $p_ID
			RETURN p2 as person
		"""
		result = db.run(query, p_ID=p_ID).data()
		return result

def get_siblings(person):
	p_ID = find_person(person)
	if not p_ID is None:
		query = """
			MATCH (p1:Person)<-[:HAS_SON | :HAS_DAUGHTER]-(:Person)-[:HAS_SON | :HAS_DAUGHTER]->(p2:Person)
			WHERE ID(p1) = $p_ID
			RETURN DISTINCT p2 as person
		"""
		result = db.run(query, p_ID=p_ID).data()
		return result

def get_grandparents(person):
	p_ID = find_person(person)
	result = []
	if not p_ID is None:
		parents = get_parents(person)
		for parent in parents:
			grandparents = get_parents(parent['person'])
			for g in grandparents:
				result.append( g )
	return result