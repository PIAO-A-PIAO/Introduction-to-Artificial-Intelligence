import os
import sys
import argparse
import pickle

def readTrainingFile(fileNames):
    words = []
    tags = []
    for name in fileNames:
        # file = open(name, "r", encoding='utf-8')
        file = open(os.path.join(os.path.dirname(__file__), name), encoding='utf-8')
        lines = file.read().splitlines()
        for line in lines:
            pair = line.split(' : ')
            words.append(pair[0])
            tags.append(pair[1])
    return words, tags

def readTestingFile(name):
    # file = open(name, "r", encoding='utf-8')
    file = open(os.path.join(os.path.dirname(__file__), name), encoding='utf-8')
    lines = file.read().splitlines()
    return lines

def breakTrainingText(words, tags):
    index = 1
    left = 0
    length = len(words)
    quoteClosed = words[0] != '\"'
    sentences = []
    sentenceTags = []

    while index < length:
        if index == length - 1:
            sentences.append(words[left:])
            sentenceTags.append(tags[left:])
            break
        if words[index] == '\"':
            if words[index + 1] not in ('s','m','re','ve','d','t') and words[index-1][-1] != 's':
                quoteClosed = not quoteClosed
                if quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index+1])
                    sentenceTags.append(tags[left:index+1])
                    left = index + 1
                elif not quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index])
                    sentenceTags.append(tags[left:index])
                    left = index
        if words[index] == '\'':
            if words[index+1] not in ('s','m','re','ve','d','t') and words[index-1][-1] != 's':
                quoteClosed = not quoteClosed
                if quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index+1])
                    sentenceTags.append(tags[left:index+1])
                    left = index + 1
                elif not quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index])
                    sentenceTags.append(tags[left:index])
        if words[index] in ('.', '?', '!'):
            if words[index + 1] not in ('\"', '\'') and quoteClosed:
                sentences.append(words[left:index+1])
                sentenceTags.append(tags[left:index+1])
                left = index + 1
        index += 1
    return sentences, sentenceTags

def breakTestingText(words):
    index = 1
    left = 0
    length = len(words)
    quoteClosed = words[0] != '\"'
    sentences = []

    while index < length:
        if index == length - 1:
            sentences.append(words[left:])
            break
        if words[index] == '\"':
            if words[index + 1] not in ('s','m','re','ve','d','t') and words[index-1][-1] != 's':
                quoteClosed = not quoteClosed
                if quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index+1])
                    left = index + 1
                elif not quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index])
                    left = index
        if words[index] == '\'':
            if words[index+1] not in ('s','m','re','ve','d','t') and words[index-1][-1] != 's':
                quoteClosed = not quoteClosed
                if quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index+1])
                    left = index + 1
                elif not quoteClosed and words[index-1] in ('.','?','!'):
                    sentences.append(words[left:index])
        if words[index] in ('.', '?', '!') and quoteClosed:
            if words[index + 1] not in ('\"', '\''):
                sentences.append(words[left:index+1])
                left = index + 1
        index += 1
    return sentences

def getProbs(sentences, sentenceTags):
    initProbs = {}    
    transProbs = {}
    transCount = {}
    obsProbs = {sentences[0][0]:{sentenceTags[0][0]:1}}
    obsCount = {sentences[0][0]:1}

    i = 0
    l = len(sentences)
    while i < l:
        words = sentences[i]
        tags = sentenceTags[i]
        index = 1
        length = len(words)

        #Initial probabilities
        if tags[0] in initProbs:
            initProbs[tags[0]] += 1
        else:
            initProbs[tags[0]] = 1

        while index < length:
            prevTag = tags[index-1]
            currTag = tags[index]
            currWord = words[index]
        
            #Transitional probabilities
            if prevTag in transProbs:
                if currTag in transProbs[prevTag]:
                    transProbs[prevTag][currTag] += 1
                else:
                    transProbs[prevTag][currTag] = 1
            else:
                transProbs[prevTag] = {currTag:1}

            if prevTag in transCount:
                transCount[prevTag] += 1
            else:
                transCount[prevTag] = 1
            
            #Observation probabilities
            if currWord in obsProbs:
                if currTag in obsProbs[currWord]:
                    obsProbs[currWord][currTag] += 1
                else:
                    obsProbs[currWord][currTag] = 1
            else:
                obsProbs[currWord] = {currTag:1}

            if currWord in obsCount:
                obsCount[currWord] += 1
            else:
                obsCount[currWord] = 1

            #Continue
            index += 1
        i += 1

    for key in initProbs:
        initProbs[key] = initProbs[key]/l

    for key in transProbs:
        for k in transProbs[key]:
            transProbs[key][k] = transProbs[key][k]/transCount[key]

    for key in obsProbs:
        for k in obsProbs[key]:
            obsProbs[key][k] = obsProbs[key][k]/obsCount[key]
    
    return initProbs, transProbs, obsProbs

def predict(sentences, initProbs, transProbs, obsProbs):
    result = []
    for sentence in sentences:
        result.append(predictTags(sentence, initProbs, transProbs, obsProbs))
    return result

def predictTags(words, initProbs, transProbs, obsProbs, k=0):
    # Initialize the matrix with the initial probabilities
    matrix = [{}]
    for tag in initProbs:
        init = initProbs[tag] if tag in initProbs else 0
        if tag in obsProbs.get(words[0], {}):
            matrix[0][tag] = {"prob": init * obsProbs[words[0]][tag], "prev": None}
        else:
            matrix[0][tag] = {"prob": init, "prev": None}

    # Iterate through the remaining words in the sequence
    for i in range(1, len(words)):
        matrix.append({})
        for tag in obsProbs.get(words[i], {}):
            maxProb = -1
            prevTag = None
            for prevTag in matrix[i - 1]:
                if tag not in transProbs[prevTag]:
                    continue
                prob = (matrix[i - 1][prevTag].get("prob", k)) * (transProbs[prevTag].get(tag, k)) * (obsProbs.get(words[i], {}).get(tag, k))
                if prob > maxProb:
                    maxProb = prob
                    prevTag = prevTag
            matrix[i][tag] = {"prob": maxProb, "prev": prevTag}

        # If the current word is unknown, use the default probabilities
        if not matrix[i]:
            maxProb = -1
            prevTag = None
            for prevTag in matrix[i - 1]:
                if tag in transProbs[prevTag]:
                    prob = matrix[i - 1][prevTag]["prob"] * transProbs[prevTag][tag]
                    if prob > maxProb:
                        maxProb = prob
                        prevTag = prevTag

                matrix[i][tag] = {"prob": maxProb, "prev": prevTag}
        
    # Find the path with the highest probability
    path = []
    maxProb, lastTag = max((matrix[-1][tag]["prob"], tag) for tag in matrix[-1])
    path.append(lastTag)
    for i in range(len(matrix) - 2, -1, -1):
        path.insert(0, matrix[i + 1][path[0]]["prev"])

    return path


if __name__ == '__main__':

    words, tags = readTrainingFile(["training1.txt"])
    sentences, sentenceTags = breakTrainingText(words, tags)
    w, t = readTrainingFile(['training2.txt'])
    s, st = breakTrainingText(w, t)

    init, trans, obs = getProbs(sentences, sentenceTags)
    testWords = readTestingFile('test2.txt')
    testSentences = breakTestingText(testWords)
    path = predict(testSentences, init, trans, obs)
    count = 0
    total = 0
    for i in range(0, len(path)):
        for j in range(0,len(path[i])):
            total += 1
            if path[i][j] == st[i][j]:
                count += 1
    print(count/total)

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--trainingfiles",
    #     action="append",
    #     nargs="+",
    #     required=True,
    #     help="The training files."
    # )
    # parser.add_argument(
    #     "--testfile",
    #     type=str,
    #     required=True,
    #     help="One test file."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file."
    # )
    # args = parser.parse_args()

    # training_list = args.trainingfiles[0]
    # words, tags = readTrainingFile(training_list)
    # sentences, sentenceTags = breakTrainingText(words, tags)
    # init, trans, obs = getProbs(sentences, sentenceTags)
    # testWords = readTestingFile(args.testfile)
    # testSentences = breakTestingText(testWords)
    # path = predict(testSentences, init, trans, obs)
    # with open(args.outputfile, 'w') as f:
    #     for i in range(0, len(path)):
    #         for j in range(0,len(path[i])):
    #             f.write(testSentences[i][j] + ' : ' + path[i][j] + '\n')
    # f.close()


    # print("training files are {}".format(training_list))

    # print("test file is {}".format(args.testfile))

    # print("output file is {}".format(args.outputfile))


    # print("Starting the tagging process.")
