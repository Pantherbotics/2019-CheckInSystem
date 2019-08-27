# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
class Member:
    times
    def __init__(self, name, idNumber):
        self.name = name
        self.idNumber = idNumber

def searchMembersList(scanID):
    for x in range(len(members)):
        if (members[x].idNumber == scanID):
            return x
    return -1    


members = []

x = True
while x:
    prompt = input("Scan card: ")
    if len(members) > 0:
        spot = searchMembersList(prompt)
        if (spot == -1):
            newMem = input("New member ( " + prompt + " ). Add name: " )
            members.append(Member(newMem, prompt))
        else:
            print("Hello " + members[spot].name)
    else:
        newMem = input("New member ( " + prompt + " ). Add name: " )
        members.append(Member(newMem, prompt))
