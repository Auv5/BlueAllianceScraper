#!/bin/env python3
import json
import collections

from http.client import HTTPConnection

def vinput(prompt, validators):
    val = validators(input(prompt).rstrip())
    while val == False:
        val = validators(input(prompt).rstrip())
    return val

def is_integer(s, silence=False):
    try:
        i = int(s)
        return s
    except ValueError:
        if not silence:
            print('[ERROR] That is not a valid integer.')
        return False

def comma_sep_ints(s, silence=False):
    if not s:
        return s

    split = s.split(',')

    for n in split:
        if not is_integer(n, True):
            if not silence:
                print('That is not a valid list.')
            return False
    return s

def main():
    print('Enter regional year:')
    year = vinput('\t--> ', is_integer)
    print('Search for regional:')
    search = vinput('\t--> ', lambda s: s)

    print('Downloading regionals...')

    conn = HTTPConnection('www.thebluealliance.com')
    conn.request('GET', '/api/v1/events/list?year=' + year)

    r = conn.getresponse()
    answer = r.read().decode('utf-8')
    data = json.loads(answer)

    matches = []

    for k in data:
        if (k['short_name'] and search.lower() in k['short_name'].lower()) or search.lower() in k['name'].lower():
            matches.append(k)

    print('\nResults:')
    index = 1
    for m in matches:
        print('\t' + str(index) + '. ' + (m['short_name'] or m['name']) + ' on ' + m['start_date'])
        index += 1

    print('\nEnter regional number:')
    number = vinput('\t--> ', is_integer)

    regional = matches[int(number)-1]

    print('Downloading event details...')

    conn.request('GET', '/api/v1/event/details?event=' + regional['key'])

    r = conn.getresponse()

    answer = r.read().decode('utf-8')
    reg_data = json.loads(answer)

    reg_teams = reg_data['teams']

    to_api = ','.join(reg_teams)

    print('Downloading team details...')

    conn = HTTPConnection('www.thebluealliance.com')
    conn.request('GET', '/api/v1/teams/show?teams=' + to_api)
    r = conn.getresponse()

    answer = r.read().decode('utf-8')

    teamdata = json.loads(answer)

    names = ['nickname', 'team_number', 'website', 'location']

    headers = ['Nickname', 'Team Number', 'Website', 'Location']

    print('\nAvailable information on teams:')

    index = 1
    for h in headers:
        print('\t' + str(index) + '. ' + headers[index-1])
        index += 1

    print('\nEnter the numbers for the information you want included (press enter for all) (Comma seperated): ')

    numbers = vinput('\t--> ', comma_sep_ints)

    usedheaders = []

    usednames = []

    if not numbers:
        numbers = ','.join(map(str,range(1,len(headers)+1)))

    nums = numbers.split(',')
    for n in nums:
        n = n.rstrip()
        usedheaders.append(headers[int(n)-1])
        usednames.append(names[int(n)-1])

    print('Please enter the name of the file you wish to write to:')

    outfname = input('\t--> ').rstrip()

    outf = open(outfname, 'w')

    outf.write(','.join(usedheaders) + ',\n')

    for i in teamdata:
        for h in usednames:
            if i[h]:
                outf.write("\"" + str(i[h]) + '\",')
            else:
                outf.write(',')
        outf.write('\n')

if __name__ == '__main__':
    main()
