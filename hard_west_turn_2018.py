#!/usr/bin/python
# coding: utf-8

"""
Hard West Turn, 2018-06-01, post-NaNoGenMo 2018 version

Copyright (c) 2018 Nick Montfort <nickm@nickm.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.

This code relies on the existence of a particular table, populated with
links to articles, in a particular English Wikipedia article. If this
article is deleted or changed, or if the ID of this table changed (as it
has since the earliest version of this program was written and run), this
code will not work as is.

code explanations: https://github.com/copilot/share/c067419c-4920-8852-a900-020ca4304191
"""

import re
from random import choice, shuffle
import urllib2
from bs4 import BeautifulSoup
from textblob import TextBlob

english = 'http://en.wikipedia.org'
simple = 'http://simple.wikipedia.org'
mass_shootings = english + '/wiki/Mass_shootings_in_the_United_States'
html = urllib2.urlopen(mass_shootings).read()
soup = BeautifulSoup(html, 'lxml')
deadliest = soup.find('span', id='Deadliest_mass_shootings').parent

incident, paragraphs, full = {}, {}, {}
links = []
litany, simple_litany, degenerate_litany = [], [], []

'Liest die Tabelle unter en.wikipedia.org/Wiki/Mass_shootings_in_the_United_States#Deadliest_mass_shootings ein'
'incident[name] = incident_link'
for row in deadliest.find_next_sibling('table', class_='wikitable').find_all('tr')[1:]:
    cells = row.find_all(['td'])
    try:
        incident_name = cells[0].text
        incident_link = cells[0].find('a')['href']
    except IndexError:
        continue
    incident[incident_name] = incident_link

para_frames = [
'This man was given to thinking of events of national importance.',
'The man thought to himself a good deal.',
'Certain things resonated in the otherwise still mind of the man.',
'Without outward sign of it, the man sometimes had a swirl of thought.',
'The man did not escape the country or himself.',
'The man went to find something, not knowing what.',
'Some things were known with certainty.',
'Some things were beyond the man’s ken.',
'The man dreamed at night sometimes, and a sliver would cut his consciousness in the morning.',
'The man may have never dreamed.',
'To forget what had been taken away, the man thought on what he knew.',
'The man had regrets.',
'The man took things moment by moment.',
'The man remembered a lot of things.',
'The man knew that some things said were fake, some facts.',
'The man knew that people said things, sometimes for no reason.',
'The man had heard a book’s worth about the events.',
'The man had many thoughts, few of them clear.',
'The man knew what he knew.',
'The man had heard things.'
]

declarations = [
'The man always had a tendency to watch, listen, and say little.',
'There was no avoiding the insistent sayings of the television.',
'The man preferred to eat alone, facing a window.',
'The man still remembered, imagined.',
'The man remained able to say all the words he needed to persist.',
'The man had been known to whittle at times.',
'The man carried an envelope of remembrances, sealed shut through pressure.',
'The man believed in opportunity.',
'The man once caught himself tapping his foot when no music was playing.',
'There was no time at which the man saw anything suspicious.',
'The man knew his place.'
]

simple_declarations = [
'It was a simple time.',
'Little held the man back.',
'The man was in a dim time.',
'The man loved his country.',
'Freedom was most important.',
'The man felt he was free.',
'Success was still somewhere before the man.',
'The man required nothing.',
'Here, the man could range.',
'The hoped for a lack of news.',
'There was nothing for the man to see or say.',
'The man was who he chose to be.'
]

with_truck = [
'He drove off in his truck',
'He got into his truck',
'His truck carried him',
'His truck was still running',
'He went off in his truck'
]

no_truck = [
'He got onto a long-distance bus',
'He gathered funds for a bus ticket',
'He managed to hitchhike',
'He found it still possible to slip into a freight train',
'He was able to walk and camp along the way'
]

laborer_job = [
'as an itinerant locksmith',
'as a night watchman',
'as a mover',
'as a day laborer',
'as a scab longshoreman',
'as a greeter'
]

unpleasant_job = [
'cleaning rough industrial spaces',
'as a dishwasher',
'as a warehouse picker',
'collecting recyclables',
'as a lookout',
'in a slaughterhouse'
]

def all_lowercase(sent, full_text):
    'Returns a suitably modified sentence if it seems to have no proper nouns.'
    if re.search(r'[a-z]', sent) and sent[0] == sent[0].upper() and \
                                     sent[1:] == sent[1:].lower():
        sent = re.sub(r'\[.*\]', '', sent)
        sent = re.sub(r'^\"$', '', sent)
        sent = re.sub(r'"', '', sent)
        sent = re.sub(r'\n', ' ', sent)
        sent = sent.strip()
        if len(sent.split()) > 2:
            first_word = sent.split()[0]
            lc_pattern = re.compile(' ' + first_word.lower() + ' ')
            uc_pattern = re.compile(r'[a-z] ' + first_word + ' ')
            if re.search(r'\:$', sent):
                return None
            elif re.search(lc_pattern, full_text):
                return sent
            elif not re.search(uc_pattern, full_text):
                return sent
            elif first_word == 'I':
                if sent[-1] == '"':
                    return '"' + sent
            else:
                second_word = sent.split()[1]
                rest = ' '.join(sent.split()[1:])[1:]
                return second_word[0].upper() + rest

'Liest die incidents ein (paragraphs, links, full)'
for i in incident:
    article = english + incident[i]
    html = urllib2.urlopen(article).read()
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', id='bodyContent')
    paragraphs[i] = []
    for p in content.find_all('p'):
        paragraphs[i].append(p.getText())
    for a in content.find_all('a'):
        href = a.get('href')
        if href is not None:
            href = href.encode('utf-8')
            if ':' not in href and re.match(r'/wiki', href):
                links.append(href)
    full[i] = content.getText()

'Arbeitet paragraphs um und addiert sie zu litany'
for i in paragraphs:
    for part in paragraphs[i]:
        blob = TextBlob(part)
        for s in blob.sentences:
            string = str(s)
            string = all_lowercase(string, full[i])
            if string is not None:
                litany.append(string)

'Liest Links aus Unterseiten (incidents) nach einem bestimmten Muster aus' 
'simple.wikipedia.org ein (new_paragraphs) und addiert sie zu simple_litany'
for count, rel_url in sorted(((links.count(e), e) for e in set(links)), reverse=True):
    if 1 < count < 14:
        article = simple + rel_url
        try:
            html = urllib2.urlopen(article).read()
            soup = BeautifulSoup(html, 'lxml')
            content = soup.find('div', id='bodyContent')
            new_paragraphs = []
            for p in content.find_all('p'):
                new_paragraphs.append(p.getText())
            for paragraph in new_paragraphs:
                blob = TextBlob(paragraph)
                for s in blob.sentences:
                    string = str(s)
                    string = all_lowercase(string, content.getText())
                    if string is not None:
                        simple_litany.append(string)
        except urllib2.HTTPError:
            continue

'Verzerrungen > degenerate_litany'
def add_to_degenerate(string):
    if ',' in string and re.findall(r'\(', string) == \
                         re.findall(r'\)', string):
        string = string.split(',')[0] + '.'
        if string[-3:] == 'm..': # Sentences ending "a.m.." and "p.m.."
            string = string[:-1]
        degenerate_litany.append(string)

'alle strings in simple_litany und litany werden verzerrt'
for string in simple_litany:
    add_to_degenerate(string)
for string in litany:
    add_to_degenerate(string)
for string in degenerate_litany:
    if ' ' in string and len(string.split()) < 5 and \
                     ',' not in string and '(' not in string:
        degenerate_litany.append(string[:-1] + ', ' + string.lower())

def print_part(statements, declare, travel, job):
    'Prints one of three parts of the book.'
    'and combines statements from litanies with previously defined declarations'
    shuffle(statements)
    tenth = int( len(statements) / 10 )
    next_para = 0
    for n in range(10):
        para = '  ' + choice(para_frames)
        for j in range(tenth):
            para += ' ' + statements[next_para + j]
            para += choice(['', '', '', '', '\n  ' + choice(para_frames)])
        print(para)
        next_para += tenth
        sentence = choice(declare)
        declare.remove(sentence)
        if len(sentence) > 0:
            sentence += ' '
        final_sentence = '  ' + sentence + choice(travel)
        if len(job) > 0:
            final_sentence += ' and he found work ' + choice(job)
        final_sentence += '.'
        print(final_sentence)

print('Hard West Turn')
print('Nick Montfort')
print('')
print('Copyright © Nick Montfort 2018; June 1, 2018 edition')
print('')
print('This output text was computer-generated using text from the English Wikipedia, en.wikipedia.org, and the Simple English Wikipedia, simple.wikipedia.org. This source text is offered under the CC-BY-SA 3.0 Unported license, so this generated text is offered under the same license.')
print('')
print(u'And the LORD said unto Satan, Whence comest thou? Then Satan answered the LORD, and said, From going to and fro in the earth, and from walking up and down in it. And the LORD said unto Satan, Hast thou considered my servant Job, that there is none like him in the earth, a perfect and an upright man, one that feareth God, and escheweth evil? Then Satan answered the LORD, and said, Doth Job fear God for nought? Hast not thou made an hedge about him, and about his house, and about all that he hath on every side? thou hast blessed the work of his hands, and his substance is increased in the land. But put forth thine hand now, and touch all that he hath, and he will curse thee to thy face.')
print('')
print(u'Near the eastern shore of the great nation a man returned to find his family already departed from the house their bank was set to seize. He thought on this with the television telling news, his little remaining liquor and less food dwindling. After four days he took what he could and set off to the west.')
print_part(litany, declarations, with_truck, laborer_job)
print('')
print('•')
print('')
print_part(simple_litany, simple_declarations, no_truck, unpleasant_job)
print('')
print('•')
print('')
for pf in para_frames:
    if len(pf) > 38:
        para_frames.remove(pf)
print_part(degenerate_litany, ['']*12, no_truck, [])
print('')
print('Spelling and punctuation corrections have been made, with U.S. spellings used throughout. Sentences beginning with proper nouns were manually removed. No other changes were made by hand to the computer-generated output.')
print('The program that generated this book is offered under a permissive free software license. Download it from nickm.com and generate your own book, modify the code, or do whatever else you like with the program:')
print('https://nickm.com/code/hard_west_turn_2018.py')
print('The program was drafted for National Novel Generation Month 2017:')
print('https://nanogenmo.github.io/')
