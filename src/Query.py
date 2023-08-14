import re
from src.utils import process_sentence, getSentences


class QueryPrase:
    def __init__(self, txtfiles):
        self.resultSet1 = []
        self.stack = None
        self.andCount = 0
        self.orCount = 0
        self.notCount = 0
        self.NumberOfDocuments = txtfiles

    def queryParsing(self, query, booleanModel):
        """
        convert user Query into
        :param query:
        :param booleanModel:
        :return:
        """
        self.stack = query.split()
        isSingleWord = bool(re.match(r"^(?!(AND|OR)).+[\w]+", query.strip()))
        isqueryOK = bool(re.match(r"^(?!(AND|OR)).+[\w/\s]+(AND|OR)[\w/\s]+", query.strip()))
        isQueryEndOK = ('AND' == self.stack[-1] or 'OR' == self.stack[-1] or 'NOT' == self.stack[-1])
        isProximty = bool(re.search(r'/(\d+)', self.stack[-1]))
        if isQueryEndOK:
            return -2
        if not isSingleWord and not isqueryOK:
            return -2
        if isSingleWord and not isqueryOK and not isQueryEndOK and not isProximty:
            process_sentence(self.stack[-1], 0, typ='q')
            try:
                resultSet = booleanModel.getPostingList(getSentences()[0])
                resultSet[0]
            except IndexError:
                return -1
            if self.stack.count('NOT') % 2:
                resultSet = self.NotOperation(resultSet)
                return resultSet
            else:
                return resultSet
        elif isqueryOK and not isQueryEndOK or isProximty:
            isProx = 0
            for _, top in enumerate(self.stack):
                if top == 'AND':
                    self.andCount = self.andCount + 1
                elif top == 'NOT':
                    self.notCount = self.notCount + 1
                elif top == 'OR':
                    self.orCount = self.orCount + 1
                elif re.search(r'/(\d+)', top):
                    isProx = isProx + 1
                else:
                    process_sentence(top, 0, typ='q')
                    self.resultSet1.append(booleanModel.getPostingList(getSentences()[0]))
            AndCount = self.stack.count('AND')
            OrCount = self.stack.count('OR')
            if self.andCount and self.andCount == AndCount+OrCount:
                for count in range(self.andCount):
                    resultSet = self.AndOperation(self.resultSet1[count], self.resultSet1[count+1])
                    self.resultSet1[count+1] = resultSet
                return resultSet
            elif self.orCount and self.orCount == AndCount+OrCount:
                for count in range(self.orCount):
                    resultSet = self.OrOperation(self.resultSet1[count], self.resultSet1[count+1])
                    self.resultSet1[count+1] = resultSet
                return resultSet
            elif self.andCount+self.orCount == AndCount+OrCount and self.andCount and self.orCount:
                idx = 0
                for count in range(self.andCount):
                    resultSet = self.AndOperation(self.resultSet1[count], self.resultSet1[count + 1])
                    self.resultSet1[count + 1] = resultSet
                    idx = count+1
                for count in range(idx, self.orCount+idx):
                    resultSet = self.OrOperation(self.resultSet1[count], self.resultSet1[count + 1])
                    self.resultSet1[count + 1] = resultSet

                return resultSet
            if isProximty and isProx:
                dist = self.stack[-1].split('/')[1]
                try:
                    resultSet = self.intersect_two_pos_proximty(self.resultSet1[0], self.resultSet1[1], dist)
                    resultSet[0]
                    return resultSet
                except IndexError:
                    return -1

    def NotOperation(self, pos1):
        """
        gave List of those document which did not contain that terms
        :param pos1:
        :return: []
        """
        answer = []
        isDict1 = type(pos1[0]) is type({})
        l1 = len(pos1)
        i = 0
        keys = []
        if isDict1:
            while i < l1:
                key1 = list(pos1[i].keys())[0]
                keys.append(key1)
                i = i + 1
            for idx in range(1, self.NumberOfDocuments + 1):
                if idx not in keys:
                    answer.append(idx)
            return answer
        else:
            for idx in range(1, self.NumberOfDocuments + 1):
                if idx not in pos1:
                    answer.append(idx)
            return answer

    def intersect_two_pos_proximty(self, lst1, lst2, dist):
        """
        search and merge those query which present with some distance
        :param lst1:
        :param lst2:
        :param dist:
        :return:
        """
        l1 = len(lst1)
        l2 = len(lst2)
        dist = int(dist)+1
        i = 0
        j = 0
        answer = []
        while i < l1 and j < l2:
            key1 = list(lst1[i].keys())[0]
            key2 = list(lst2[j].keys())[0]
            if key1 == key2:
                value1 = list(lst1[i].values())[0]
                value2 = list(lst2[j].values())[0]
                for val1 in value1:
                    for val2 in value2:
                        if abs(val1 - val2) <= dist:
                            if key1 not in answer:
                                answer.append(key1)
                i = i + 1
                j = j + 1
            elif key1 > key2:
                j = j + 1
            else:
                i = i + 1
        return answer

    def OrOperation(self, pos1, pos2):
        """
        Merge two terms posting list Means Union of two terms
        :param pos1:
        :param pos2:
        :return:
        """
        answer = []
        isDict1 = type(pos1[0]) is type({})
        isDict2 = type(pos2[0]) is type({})
        l1 = len(pos1)
        l2 = len(pos2)
        i = 0
        j = 0
        while i < l1 and j < l2:
            if isDict1 and isDict2:
                key1 = list(pos1[i].keys())[0]
                key2 = list(pos2[j].keys())[0]
            elif not isDict1 and not isDict2:
                key1 = pos1[i]
                key2 = pos2[j]
            elif not isDict1 and isDict2:
                key1 = pos1[i]
                key2 = list(pos2[j].keys())[0]
            else:
                key1 = list(pos1[i].keys())[0]
                key2 = pos2[j]
            if key1 == key2:
                answer.append(key1)
                i = i + 1
                j = j + 1
            elif key1 > key2:
                answer.append(key2)
                j = j + 1
            else:
                answer.append(key1)
                i = i + 1
        while i < l1:
            if isDict1:
                key1 = list(pos1[i].keys())[0]
            else:
                key1 = pos1[i]
            answer.append(key1)
            i = i + 1
        while j < l2:
            if isDict2:
                key2 = list(pos2[j].keys())[0]
            else:
                key2 = pos2[j]
            answer.append(key2)
            j = j + 1
        return answer

    def AndOperation(self, pos1, pos2):
        """
        Intersection Of Two posting List
        :param pos1:
        :param pos2:
        :return:
        """
        answer = []
        isDict1 = type(pos1[0]) is type({})
        isDict2 = type(pos2[0]) is type({})
        l1 = len(pos1)
        l2 = len(pos2)
        i = 0
        j = 0
        while i < l1 and j < l2:
            if isDict1 and isDict2:
                key1 = list(pos1[i].keys())[0]
                key2 = list(pos2[j].keys())[0]
            elif not isDict1 and not isDict2:
                key1 = pos1[i]
                key2 = pos2[j]
            elif not isDict1 and isDict2:
                key1 = pos1[i]
                key2 = list(pos2[j].keys())[0]
            else:
                key1 = list(pos1[i].keys())[0]
                key2 = pos2[j]
            if key1 == key2:
                answer.append(key1)
                i = i + 1
                j = j + 1
            elif key1 > key2:
                j = j + 1
            else:
                i = i + 1

        return answer




