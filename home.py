import glob
from src.utils import __init__, process_sentence, getSentences
from src.Query import QueryPrase
from src.BooleanModel import BooleanModel

path = "data"

__init__()

txtfiles = []
# get all text files in txtfiles list
for file in glob.glob(path + "\\*.txt"):
    txtfiles.append(file.split('\\')[-1])

index = 1
# read each file data preprocess the data and store in an array
for _, file in enumerate(txtfiles):
    docId = int(file.split('.')[0])
    with open("data\\" + file, 'r') as f:
        line = f.readline()
        while line:
            line = line.strip()
            if len(line) > 0:
                index = process_sentence(line, docId, idx=index)
            line = f.readline()
    index = 1

# sort the list of tuple first by terms and then by docID
sorted_tuple_Array = sorted(getSentences(), key=lambda element: (element[0], element[1]))
booleanModel = BooleanModel()
booleanModel.create_inverted_index(sorted_tuple_Array)


def handleQuery(query):
    queryParse = QueryPrase(len(txtfiles))
    result = queryParse.queryParsing(query, booleanModel)
    if result == -1:
        return [-1]
    elif result == -2:
        return [-2]
    else:
        return result

