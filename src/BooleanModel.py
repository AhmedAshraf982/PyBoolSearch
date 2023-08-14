from os import path
import json

class BooleanModel():
    def __init__(self):
        self.inverted_index = {}

    def create_inverted_index(self, sorted_tuple_array):
        """
            create invertedIndex using dictionary which contain key means terms
            and value contain list of dictionary which contain key means docID and
            value contain list of position  when the word occur in that document
            {
                term1:[{docId:[position1, position2]},{docId:[position1, position2]}],
                term2:[{docId:[position1, position2]},{docId:[position1, position2]}]
            }
            """
        # if path.isfile('./src/invertedAndPositionalIndex.json'):
        #     self.loadDict()
        #     print(self.inverted_index)
        #     return
        for _, values in enumerate(sorted_tuple_array):
            if values[0] not in self.inverted_index:
                self.inverted_index[values[0]] = [{values[1]: [values[2]]}]
            else:
                idx = next(
                    (index for (index, value) in enumerate(self.inverted_index[values[0]]) if
                     values[1] in list(value)), None)
                if idx is None:
                    self.inverted_index[values[0]].append({values[1]: []})
                    idx = next(
                        (index for (index, value) in enumerate(self.inverted_index[values[0]]) if
                         values[1] in list(value)),
                        None)
                self.inverted_index[values[0]][idx][values[1]].append(values[2])
        self.storeDict()
        return

    def loadDict(self):
        with open("./src/invertedAndPositionalIndex.json", 'r') as f:
            self.inverted_index = json.load(f)

    def storeDict(self):
        with open("./src/invertedAndPositionalIndex.json", 'w') as f:
            json.dump(self.inverted_index, f)


    def getPostingList(self, term):
        try:
            result = self.inverted_index[term]
            return result
        except KeyError:
            result = []
            return result
