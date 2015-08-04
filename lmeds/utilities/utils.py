'''
Created on Nov 17, 2013

@author: timmahrt
'''


def detectLineEnding(txt):
    returnText = None  # A file may have no newlines
    endingsList = ["\r\n", "\n", "\r"]
    truthList = []
    
    for lineEnding in endingsList:
        truthList.append(lineEnding in txt)
        if lineEnding in txt:
            returnText = lineEnding
            break
            
    # Obviously, this will not be true if the line ending is "\r\n"
    # -- I'm not sure what I intended with this piece of code
#     assert(sum(truthList) <= 1)
    
    return returnText
