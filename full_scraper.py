#!/bin/env python3
import json
import traceback
import argparse

from http.client import HTTPConnection
from datetime import date

DEF_HEADERS = {'User-Agent': 'TrueBlue bluealliance Scraper',
        'X-TBA-App-Id': 'frc2994:scouting:v1'}

def vinput(prompt, validator, default=None):
    if default:
        prompt = prompt + ' [' + default + ']:'
    else:
        prompt += ':'
    print(prompt)
    rawin = input('\t--> ').rstrip()
    val = validator(rawin)
    while rawin and val == False:
        rawin = input('\t--> ').rstrip()
        val = validator(rawin)
    if rawin or not default:
        return rawin
    else:
        return default


def is_integer(s, silence=False):
    try:
        int(s)
        return s
    except ValueError:
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
    today = date.today()
    year = today.year
    if today.month > 3:
       year += 1
    year = vinput('Enter regional year', is_integer, str(year))
    search = vinput('Search for regional', lambda s: s)

    print('Downloading regionals...')

    conn = HTTPConnection('www.thebluealliance.com')
    conn.request('GET', '/api/v1/events/list?year=' + year, headers=DEF_HEADERS)

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

    number = vinput('\nEnter regional number', is_integer, '1')

    regional = matches[int(number)-1]

    print('Downloading event details...')

    conn.request('GET', '/api/v1/event/details?event=' + regional['key'], headers=DEF_HEADERS)

    r = conn.getresponse()

    answer = r.read().decode('utf-8')
    reg_data = json.loads(answer)

    reg_teams = reg_data['teams']

    to_api = ','.join(reg_teams)

    print('Downloading team details...')

    conn = HTTPConnection('www.thebluealliance.com')
    conn.request('GET', '/api/v1/teams/show?teams=' + to_api, headers=DEF_HEADERS)
    r = conn.getresponse()

    answer = r.read().decode('utf-8')

    teamdata = json.loads(answer)

    names = ['team_number', 'nickname', 'website', 'location']

    headers = ['Team Number', 'Nickname', 'Website', 'Location']

    print('\nAvailable information on teams:')

    index = 1
    for h in headers:
        print('\t' + str(index) + '. ' + headers[index-1])
        index += 1

    numbers = vinput('\nEnter the numbers for the information you want included (comma seperated)', comma_sep_ints, ','.join(map(str, range(1, len(headers)+1))))

    usedheaders = []

    usednames = []

    nums = numbers.split(',')
    for n in nums:
        n = n.rstrip()
        usedheaders.append(headers[int(n)-1])
        usednames.append(names[int(n)-1])

    outfname = vinput('Please enter the name of the file you wish to write to', lambda s: s, regional['key'] + '.csv')

    outf = open(outfname, 'w')

    outf.write(','.join(usedheaders) + ',\n')

    for i in teamdata:
        for h in usednames:
            if i[h]:
                outf.write("\"" + str(i[h]).replace('"', '').replace(',', '') + '\",')
            else:
                outf.write(',')
        outf.write('\n')

VERBOSE = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--verbose', help='If an error occurred, show verbose input.', action='store_true')

    args = parser.parse_args()

    VERBOSE = args.verbose
    if VERBOSE:
        print('Verbosity enabled.')

    try:
        main()
    except:
        if not VERBOSE:
            print('\n\nAn error occurred. Please send me an email '
                  '(controls.leadstu@team2994.ca) with the details from --verbose. :)')
        else:
            traceback.print_exc()
