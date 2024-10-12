import requests
import sys
import utils

maps_api_key = "AIzaSyBCeaO2L588Nurh93ykNesDensqTsN0rR4"

def get_request(url, params):
    response = requests.get(url, params=params)
    data = {}

    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")
        exit()

    return data

def request_all(url, params, inc_func):
    all_data = []
    while(True):
        response = requests.get(url, params=params)
        data = {}
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Error requesting page: {response.status_code}")
            exit()

        if not data or len(data) == 0:
            break

        all_data.extend(data)
        inc_func(params)
    return all_data

def request_all_courses():
    url = f"https://api.umd.io/v1/courses"
    params = {"sort": "course_id", 
                  "semester": 202501, 
                  "per_page": 100, 
                  "page": 1,
                  "expand": "sections"}
    def inc_func(dic):
        dic["page"] += 1
    res = request_all(url, params, inc_func)
    return array_to_dic(res, "course_id")

def request_all_professors():
    url = "https://planetterp.com/api/v1/professors"
    params = {"offset": 0,
              "type": "professor"}
    def inc_func(param):
        param["offset"] += 100
    res = request_all(url, params, inc_func)
    return array_to_dic(res, "name")

def request_all_buildings():
    url = "https://api.umd.io/v1/map/buildings"
    params = {}
    res = get_request(url, params) 
    return array_to_dic(res, "code")

def request_graph():
    from osmnx import graph_from_point

    center = (38.9869, -76.9426) # UMD College Park 
    graph = graph_from_point(center, dist=1000, network_type="walk")
    return graph

def nearest_nodes(buildings, graph):
    from osmnx.distance import nearest_nodes

    dic = {}
    for b_id, building in buildings.items():
        id = b_id
        long = float(building["long"])
        lat = float(building["lat"])
        nearest = nearest_nodes(graph, long, lat)
        dic[id] = nearest
    return dic

def request_all_distances():
    from networkx import shortest_path_length

    buildings = utils.read_data_from_json("data/building_data.json")
    graph = read_graph_from_file("data/graph_data.graphml")

    nearest_dic = nearest_nodes(buildings, graph)
    distances = {}
    for b1 in buildings.keys():
        start = nearest_dic.get(b1)
        lengths = shortest_path_length(graph, start, weight="length")
        distances[b1] = {}
        for b2 in buildings.keys():
            end = nearest_dic.get(b2)
            distances[b1][b2] = lengths[end]
    return distances

def write_graph_to_file(graph, file_name):
    from osmnx import save_graphml

    save_graphml(graph, filepath=file_name)

def read_graph_from_file(file_name):
    from osmnx import load_graphml

    return load_graphml(filepath=file_name)

# useful for O(1) lookups later
def array_to_dic(arr, by_key):
    return {item[by_key]: {key: value for key, value in item.items() if key != by_key} for item in arr}

name = sys.argv[0]
funcs = {"course": request_all_courses, 
         "building": request_all_buildings,
         "professor": request_all_professors,
         "graph": request_graph,
         "distance": request_all_distances}

if len(sys.argv) != 2 or sys.argv[1] not in funcs:
    print(f"Error: Expected argument <course|building|professor|graph|distance>")
    sys.exit()

request = sys.argv[1]
f = funcs[request]
file = f"data/{request}_data"
data = f() 

if request == "graph":
    file += ".graphml"
    write_graph_to_file(data, file)
else:
    file += ".json"
    utils.write_data_to_json(data, file)


print(f"Successfully wrote {sys.argv[1]} data to file {file}")
