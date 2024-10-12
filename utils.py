import json

def sort(all_data, by_key):
    return sorted(all_data, key=lambda x: x[by_key])

def binary_search(all_data, key, val):
    l=0
    r=len(all_data)-1
    while(l <= r):
        c = (l+r)//2
        cur_val = all_data[c].get(key)
        if val == cur_val:
            return all_data[c]
        elif val < cur_val:
            r = c-1
        else:
            l = c+1
    return None

def write_data_to_json(data, file_name):
    try:
        out_file = open(file_name, "w")
    except Exception:
        raise Exception(f"Failed to open file {file_name} for writing")
    json.dump(data, out_file, indent=4)

def append_data_to_json(data, file_name):
    try:
        out_file = open(file_name, "a")
    except Exception:
        raise Exception(f"Failed to open file {file_name} for appending")
    json.dump(data, out_file, indent=4)

def read_data_from_json(file_name):
    try: 
        in_file = open(file_name, "r")
    except Exception:
        raise Exception(f"Failed to open file {file_name} for reading")
    data = json.load(in_file)
    return data

