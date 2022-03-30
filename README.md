# graph-database

Simple genealogical tree implementation within graph database and flask [project for "Data processing in computing clouds"]. 

**https://genealogical-tree-1121.herokuapp.com/**

---

## Table of contents
1. [Project description](#description)
2. [Assumptions](#assumptions)

---

## 1. Project description <a name="description"></a>

The aim of this project was to create a simple web application presenting usage of the graph database [*Neo4j*](https://neo4j.com/), 
which would be uploaded into some cloud service (*Heroku* in this case), and subject - genealogical tree.
Application allows user to add new person to database (with relationships indicated by the user), find relationship between two people
and to present data in the simplest possible way - with table and graph.

All nodes are type `Person` and consist of 3 mandatory attributes:
- `fname` - first name
- `lname` - last name
- `born` - birth year
- `died` - death year (optional).

There can be a few types of relationships between the nodes:
- `MARRIED` - marriage (contains additional parameter `since` indicating the year of marriage)
- `HAS_CHILD` - relation parent-child <br>
**Note: For testing data there is additional division:**
    - `HAS_SON` - relation parent-son
    - `HAS_DAUGTHER` - relation parent-daughter 
    
  **so that visualisation of finding relationships could be more attractive (this feature could be further developed in the future).**

---

## 2. Assumptions <a name="assumptions"></a>

**This is *proof of concept* type of project** which means it's simplified, limited and has some assumptions made:
- input data are valid and are of proper type (implemented validation is basic)
- people with identical: first name, last name and birth year cannot be in database **at once**
- neither sex nor gender implemented 
- between 2 nodes there can only be one type of relationship
- functionality and complexity of data is limited to presenting general idea/usage of graph database
- number of entries (people) should be as small as possible for better quality of plotting graph (otherwise it would become unreadable)
- plotting is made with Python module [`networkx`](https://networkx.org/), what brings some consequences: it's relatively easy in implementation, however layout of whole structure (positioning of nodes and relationships with their attributes) leaves a lot to be desired, nevertheless main functionality has been kept in order to graphically validate operations 
- majority of methods as well as artwork on this webpage are rather straightforward and minimalistic (bear in mind **this is *proof of concept* type of project**).
