#!/usr/bin/python

import sys
import csv
from ranking import *
from tabulate import tabulate
import os
from num2words import num2words
import locale
locale.setlocale( locale.LC_ALL, '' )
import fractions
import datetime
import requests
from bs4 import BeautifulSoup
import argparse
import sqlite3

races = {}
race_descriptions = {}
race_surfaces = {}
race_distances = {}
race_claim_prices = {}
race_classes = {}
morning_lines = {}
race_purses = {}
race_class_code = {}
race_date = ''
race_track = ''
winners_dict = {}
class_rankings = {
"GStk": 5,
"STK": 5,
"SST": 5,
"Stk": 5,
"HDS": 5,
"ALW":	4,
"Alw":	4,
"HCP":	4,
"Hcp":	4,
"AN1Y":	4,
"AN2X":	4,
"AN1X":	4,
"AN2L":	3,
"AN3L":	3,
"AOC":	3,
"STR":	3,
"FTR":	3,
"FUT":	3,
"SHP":	3,
"OClN": 3,
"OCL":	3,
"SOC":	3,
"WCL":	2,
"ClmN":	2,
"CLM":	2,
"Clm":	2,
"MDN":	2,
"FNL":	2,
"MSW":	2,
"MOC":	2,
"WMC":	1,
"MCL":	1,
"Maid":	1,
"TRL": 1,
"DBY": 1,
"DTR": 1


}

non_scrub_tracks = {
    'Dmr': 61,
    'DMR': 61,
    'SA': 61,
    'Kee': 61,
    'KEE': 54,
    'PrM': 34,
    'GG': 36,
    'LA': 35,
    'Alb': 35,
    'Leo': 61,
    'Bel': 61,
    'CD': 61,
    'GP': 61,
    'GPW': 61,
    'Sar': 61,
}

track_abbreviations = {
    'Dmr': 61,
    'DMR': 61,
    'SA': 61,
    'Zia': 61,
    'Kee': 61,
    'KEE': 54,
    'PrM': 34,
    'GG': 61,
    'LA': 35,
    'Alb': 35,
    'Leo': 61,
    'Bel': 61,
    'CD': 61,
    'GP': 61,
    'GPW': 61,
    'Sar': 61,
    'Del': 37,
    'Prx': 55,
    'Cnl': 36,
    'Mil': 36,
    'Ind': 36,
    'LRC': 36,
    'Lrl': 54,
    'ElP': 54,
    'KD': 54,
    'AP': 54,
    'WO': 61,
    'Pim': 61,
    'Cur': 54,
    'CT': 54,
    'NEW': 54,
    'DON': 54,
    'LCH': 54,
    'GOO': 54,
    'CHY': 54,
    'DEA': 54,
    'Mth': 54,
    'NBY': 54,
    'Nag': 54,
    'Tok': 54,
    'ASC': 54,
    'Bad': 54,
    'EmD': 54,
    'Hst': 54,
    'TuP': 54,
    'Cby': 54,
    'BtP': 54,
    'RP': 54,
    'LaD': 54,
    'LS': 54,
    'Mey': 54,
    'PID': 54,
    'SAL': 54,
    'OP': 54,
    'FL': 30,
    'Aqu': 61,
    'HAR': 54,
    'Pen': 54,
    'Tam': 54,
    'Rom': 54,
    'Tip': 54,
    'FP': 54,
    'FG': 54,
    'FE': 54,
    'WRD': 54,
    'Tdn': 54,
    'Mnr': 54,

}

class Race:
    description = ''
    horses = []
    race_number = 0
    early_rate_rankings = []
    max_beyer_rankings = []
    avg_beyer_rankings = []
    last_beyer_rankings = []
    jockey_rankings = []
    chances_rankings = []
    improvement_rankings = []
    loss_distance_rankings = []
    money_rate_rankings = []
    cur_year_earnings_rankings = []
    class_value = 0
    track_code = ''
    trainer_rankings = []
    sale_rankings = []
    works_rankings = []
    surface = ''
    maiden_trainer_rankings = []
    maiden_works_rankings = []
    maiden_sale_rankings = []
    claim_value = 0
    race_class = ''
    race_purse = ''
    race_date = ''
    max_wins = 0

    def __init__(self, track_code, race_number, class_value, distance, race_class, race_purse, race_date, surface):
        self.track_code = track_code
        self.race_number = race_number
        self.horses = []
        self.avg_beyer_rankings = []
        self.max_beyer_rankings = []
        self.last_beyer_rankings = []
        self.early_rate_rankings = []
        self.jockey_rankings = []
        self.chances_rankings = []
        self.improvement_rankings = []
        self.loss_distance_rankings = []
        self.score_rankings = []
        self.cur_year_earnings_rankings = []
        self.class_value = class_value
        self.money_rate_rankings = []
        self.trainer_rankings = []
        self.money_rate_rankings = []
        self.works_rankings = []
        self.maiden_trainer_rankings = []
        self.maiden_works_rankings = []
        self.maiden_sale_rankings = []
        self.distance = distance
        self.race_class = race_class
        self.race_purse = race_purse
        self.race_date = race_date
        self.surface = surface

    def __repr__(self):
        return repr(self.horses)


class Horse:
    name = ''
    early_rate = 0.0
    wins = 0
    show = 0
    place = 0
    come_back = 0
    jockey = 0.0
    jockey_second = 0.0
    layoff = 0
    race = 0
    pps = []
    bonuses = []
    max_beyer = 0
    avg_beyer = 0
    chances_rate = 0.0
    lifetime_starts = 0
    post = 0
    aggregate = 0.0
    morning_line = ''
    long_shot = False
    improvement_rate = 0.0
    form_bonus = False
    down_class = 0
    down_track = False
    sale = 0
    trainer_pct = 0.0
    fluke = False
    won_last = False
    ops = 0.0
    super_gain = False
    zags = 0
    loss_distance = 0.0
    works = 0.0
    closing_speed = False
    last_beyer = 0.0
    dan_odds = 0.0
    cur_year_earnings = 0.0
    money_rate = 0.0
    implied_probability = 0.0
    stars = 0
    best_result_at_distance = -1
    best_result_at_comp = ''
    jockey_name = ''
    previous_jockey_name = ''
    maiden_lock = False
    had_bullet = False
    top_class = ''
    top_class_finish = ''
    max_position = ''
    dist_change = 0
    comp_race = ''
    pen_rate = 0.0
    max_beyer_days_ago = 0
    last_odds = 0.0
    last_odds_pos = 0
    avg_odds = 0.0
    def __init__(self, name, early_rate, max_beyer, max_beyer_days_ago, avg_beyer, jockey, jockey_second, chances_rate, lifetime_starts, post,
                 morning_line,
                 wins, place, show, improvement_rate, form_bonus, down_class, sale, trainer_pct, fluke, won_last, down_track,super_gain,zags,
                 loss_distance, closing_speed,last_track,works, had_bullet, last_beyer, cur_year_earnings, stars, best_result_at_distance,
                 jockey_name, previous_jockey_name, maiden_lock, tom_dist,tom_turf,tom_mud, last_finish, last_finish_distance, layoff, max_position, best_result_at_comp,
                 dist_change, pen_rate, last_odds, last_odds_pos, avg_odds):
        self.name = name
        self.early_rate = early_rate
        self.max_beyer = max_beyer
        self.max_beyer_days_ago = max_beyer_days_ago
        self.avg_beyer = avg_beyer
        self.jockey = jockey
        self.jockey_second = jockey_second
        self.chances_rate = chances_rate
        self.lifetime_starts = lifetime_starts
        self.post = post
        self.aggregate = 0.0
        self.morning_line = morning_line
        self.long_shot = False
        self.wins = wins
        self.place = place
        self.show = show
        self.improvement_rate = improvement_rate
        self.form_bonus = form_bonus
        self.down_class = down_class
        self.down_track = down_track
        self.bonuses = []
        self.trainer_pct = trainer_pct
        self.sale = sale
        self.fluke = fluke
        self.won_last = won_last
        self.ops = 0.0
        self.super_gain = super_gain
        self.zags = zags
        self.loss_distance = loss_distance
        self.closing_speed = closing_speed
        self.last_track = last_track
        self.works = works
        self.last_beyer = last_beyer
        self.cur_year_earnings = cur_year_earnings
        self.money_rate = float((int(wins) + int(place) + int(show))) / int(lifetime_starts) if int(lifetime_starts) > 0 else 0.0
        self.stars = stars
        self.best_result_at_distance = best_result_at_distance
        self.jockey_name = jockey_name
        self.previous_jockey_name = previous_jockey_name
        self.maiden_lock = maiden_lock
        self.had_bullet = had_bullet
        self.tom_dist = tom_dist
        self.tom_turf = tom_turf
        self.tom_mud = tom_mud
        self.last_finish = last_finish
        self.last_finish_distance = last_finish_distance
        self.layoff = layoff
        self.max_position = max_position
        self.dist_change = dist_change
        self.comp_race = best_result_at_comp
        self.pen_rate = pen_rate
        self.last_odds = last_odds
        self.last_odds_pos = last_odds_pos
        self.avg_odds = avg_odds

    def __repr__(self):
        return repr(self.name + ' : ' + str(self.early_rate) + ':' + str(self.max_beyer) + ':' + str(self.avg_beyer))


def get_works(horse_name):
    works = []
    with open(sys.argv[1] + '.cw', 'r') as f:
        for row in csv.reader(f):
            if horse_name == row[3]:
                works.append(row)
    return works[:8]

def get_pps(horse_name):
    pps = []
    with open(sys.argv[1] + '.chr', 'r') as f:
        for row in csv.reader(f):
            if horse_name == row[3]:
                pps.append(row)
    return pps[:8]

def get_special_products(horse_name):
    with open(sys.argv[1] + '.cs', 'r') as f:
        for row in csv.reader(f):
            if horse_name == row[3]:
                return row



def get_improvement_rate(pps):
    total = 0.0
    for pp in pps:
        if (float(pp[53]) < float(pp[51]) and (float(pp[50]) != 1 and float(pp[52]) != 1)):
            total += 1
        elif (float(pp[51]) < float(pp[53]) and (float(pp[50]) == 1 and float(pp[52]) == 1)):
            total += 1
        elif (float(pp[50]) != 1) and (float(pp[52]) == 1):
            total += 1
    return total / len(pps)


def get_early_rate(pps):
    total = 0.0
    for pp in pps:
        if float(pp[47]) <= 2.0 or float(pp[46]) == 1:
            total += 1
    return total / len(pps)


def get_pen_rate(pps):
    pen_total = 0.0
    for pp in pps:
        pen_total += float(pp[51])
    return pen_total / len(pps)


def get_best_result_at_distance(pps, distance):
    cur_best = 100
    for pp in pps:
        if float(distance) == float(pp[12]):  # same distacne
            if float(pp[52]) < cur_best:
                cur_best = float(pp[52])
    if cur_best != 100:
        return cur_best
    else:
        return -1


def get_best_result_at_comp(pps, race_class, claim_price):
    cur_best = 100
    best_string = ''
    for pp in pps:
        if race_class == pp[13] and float(claim_price) == float(pp[15]):
            if int(pp[52]) < cur_best:
                cur_best = int(pp[52])
                best_string = '%s (%s) %s %s %s %s ' % (num2words(pp[52],to='ordinal_num'),pp[57], pp[53] , pp[6], pp[7], pp[14])

    return best_string

def get_closing_speed(pps):
    closing_speed = False
    for pp in pps:
        if int(pp[50]) != 1:
            if int(pp[52]) == 1:
                if float(pp[51]) + float(pp[53]) > 4:
                    closing_speed = True
                    break
            elif float(pp[51]) - float(pp[53]) > 4:
                closing_speed = True
    return closing_speed

def get_max_beyer(pps):
    max_beyer = 0
    today = datetime.datetime.now()
    max_beyer_days_ago = 0
    for pp in pps:
        speed_figure = int(pp[57])
        if pp[10] == '-':
            speed_figure -= 14
        if speed_figure > max_beyer and speed_figure not in [998, 999]:
            max_beyer = speed_figure
            datetime_object = datetime.datetime.strptime(pp[6], '%m/%d/%Y')
            max_beyer_days_ago = (today - datetime_object).days

    return max_beyer, max_beyer_days_ago


def get_form_bonus(pps):
    if int(pps[0][57]) in [998,999] or int(pps[1][57]) in [998,999] or int(pps[2][57]) in [998,999]:
        return False
    if int(pps[0][57]) > int(pps[1][57]) + 3 > int(pps[2][57]) + 3:
        return True
    else:
        return False

def get_works_rate(works):
    had_bullet = False
    num_works = 0
    total = 0.0
    average = 0.0
    for work in works:
        if(work[12] == 'Y'):
            had_bullet = True
        if int(work[15]) > 10:
            num_works += 1
            total -= (float(work[14]) / float(work[15]))
    if num_works > 0:
        average = total / num_works
        return (average, had_bullet)
    else:
        return (0.0, False)

def get_super_gain(pps):
    if int(pps[0][57]) - int(pps[1][57]) >= 13 and int(pps[1][57]) > 30 and int(pps[0][52]) in [1,2,3]:
        return True
    else:
        return False


def get_fluke(pps):
    if int(pps[1][57]) - int(pps[0][57]) >= 15:
        return True
    return False


def get_zags(pps):
    zags = 0
    for pp in pps:
        if int(pp[48]) > 0:
            third_check = int(pp[48])
        else:
            third_check = int(pp[46])
        if third_check < int(pp[50]) > int(pp[52]):
            zags += 1
    return zags


def get_avg_beyer(pps):
    average_beyer = 0
    total = 0
    min = int(pps[0][57])
    for pp in pps:
        if int(pp[57]) not in [998, 999, -1]:
            if int(pp[57]) < min:
                min = int(pp[57])
            speed_figure = int(pp[57])
            if pp[10] == '-': # timeform
                speed_figure -= 14
            average_beyer += speed_figure
            total += 1
    if total > 3: # have 4 to qualify tossing the lowest
        average_beyer -= min
        total -= 1
        return average_beyer / total
    else:
        return 0


def max_class_and_finish(pps):
    max_class_rank = class_rankings[pps[0][13]]
    max_class_string = pps[0][13]
    best_position = int(pps[0][52])
    for pp in pps:
        this_class_string = pp[13]
        this_class_rank = class_rankings[this_class_string]
        if this_class_rank < max_class_rank:
            continue
        elif this_class_rank == max_class_rank:  # check finish
            if int(pp[52]) > best_position:
                continue
            else:
                best_position = int(pp[52])
        else:
            max_class_rank = this_class_rank
            max_class_string = this_class_string
            best_position = int(pp[52])

    return (max_class_string, best_position)

def get_chances_rate(pps):
    chances = 0.0
    total = 0.0
    for pp in pps:
        if int(pp[50]) == 1 or float(pp[51]) <= 4:
            chances += 1
    return chances / len(pps)


def get_loss_distances(pps):
    loss_distance = 0.0
    total = 0.0
    for pp in pps:
        if int(pp[52]) != 1:
            loss_distance += float(pp[53])
            total += 1
    if total > 0:
        return loss_distance / total
    else:
        return 99

def profile_horse(horse, race_class, race_distance, avg_delta, max_delta, last_delta):
    profile_hits = 0
    con = sqlite3.connect('db4.db')
    cur = con.cursor()
    #print horse.name
    cur.execute("SELECT avg(\"Works\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
    works_db = cur.fetchone()[0]
    if works_db <= float(horse.works) and float(horse.works) != 0 and float(horse.works) < 0 and works_db:
        profile_hits += 1
        #print "works:", works_db, horse.works

    if horse.lifetime_starts > 0:
        cur.execute("SELECT avg(\"Last Finish\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
        lf_db = cur.fetchone()[0]
        if not lf_db:
            cur.execute(
                "SELECT avg(\"Last Finish\") FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
                horse.down_class, race_class))
            lf_db = cur.fetchone()[0]

        if lf_db >= int(horse.last_finish):
            profile_hits += 1
            #print "last finish place:", lf_db, horse.last_finish

        cur.execute("SELECT avg(\"Last Finish Distance\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
        lfd_db = cur.fetchone()[0]
        if not lfd_db:
            cur.execute(
                "SELECT avg(\"Last Finish Distance\") FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
                horse.down_class, race_class))
            lfd_db = cur.fetchone()[0]
        if lfd_db >= float(horse.last_finish_distance):
            profile_hits += 1
            #print "last finish distance:", lfd_db, horse.last_finish_distance

        cur.execute("SELECT avg(Trainer) FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
        trainer_db = cur.fetchone()[0]
        if not trainer_db:
            cur.execute(
                "SELECT avg(Trainer) FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
                horse.down_class, race_class))
            trainer_db = cur.fetchone()[0]
        if trainer_db <= float(horse.trainer_pct):
            profile_hits += 1
            #print "trainer", trainer_db, horse.trainer_pct

        cur.execute("SELECT avg(Jockey) FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
        jockey_db = cur.fetchone()[0]
        if not jockey_db:
            cur.execute(
                "SELECT avg(Jockey) FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
                horse.down_class, race_class))
            jockey_db = cur.fetchone()[0]

        if jockey_db <= float(horse.jockey):
            profile_hits += 1
            #print "jockey", jockey_db, horse.jockey


    elif horse.lifetime_starts == 1:
        cur.execute("SELECT avg(\"Last Finish\") FROM races where \"Lifetime Starts\" = 1")
        last_finish_db = cur.fetchone()[0]
        if last_finish_db >= float(horse.last_finish):
            profile_hits += 1
            #print "last_finish place 1 race", last_finish_db, horse.last_finish


        if float(horse.last_finish_distance) <= 8:
            profile_hits += 1

        cur.execute("SELECT avg(\"Last Finish Distance\") FROM races where \"Lifetime Starts\" = 1")
        last_finish_distance_db = cur.fetchone()[0]
        if last_finish_distance_db >= horse.last_finish_distance:
            profile_hits += 1
            #print "last finish distance:"

        cur.execute("SELECT avg(Trainer) FROM races where \"Lifetime Starts\" = 1")
        trainer_db_0 = cur.fetchone()[0]
        if trainer_db_0 <= float(horse.trainer_pct):
            profile_hits += 1
            #print "trainer 1", trainer_db_0, horse.trainer_pct

        cur.execute("SELECT avg(\"Tom Dist\") FROM races where \"Distance\" = %s" % race_distance)
        tom_dist_db = cur.fetchone()[0]
        if tom_dist_db <= int(horse.tom_dist):
            profile_hits += 1
            #print "tom dist 1 ", tom_dist_db, horse.tom_dist


    elif horse.lifetime_starts == 0:
        cur.execute("SELECT avg(Jockey) FROM races where \"Lifetime Starts\" = 0")
        jockey_db_0 = cur.fetchone()[0]
        if jockey_db_0 <= float(horse.jockey):
            profile_hits += 1
            #print "jockey db0", jockey_db_0, horse.jockey
        cur.execute("SELECT avg(Trainer) FROM races where \"Lifetime Starts\" = 0")
        trainer_db_0 = cur.fetchone()[0]
        if trainer_db_0 <= float(horse.trainer_pct):
            profile_hits += 1
            #print "trainer"
        cur.execute("SELECT avg(\"Tom Dist\") FROM races where \"Distance\" = %s" % race_distance)
        if isinstance(horse.tom_dist,int):
            if cur.fetchone()[0] <= int(horse.tom_dist):
                profile_hits += 1


    cur.execute("SELECT avg(\"Max B. Delta\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
    max_b_delta_db = cur.fetchone()[0]
    if not max_b_delta_db:
        cur.execute(
            "SELECT avg(\"Max B. Delta\") FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
            horse.down_class, race_class))
        max_b_delta_db = cur.fetchone()[0]

    if max_b_delta_db <= max_delta:
        profile_hits += 1
        #print "max beyer delta", max_b_delta_db, max_delta

    cur.execute("SELECT avg(\"Avg. B. Delta\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
    avg_b_delta_db = cur.fetchone()[0]
    if not avg_b_delta_db:
        cur.execute(
            "SELECT avg(\"Avg. B. Delta\") FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
            horse.down_class, race_class))
        avg_b_delta_db = cur.fetchone()[0]

    if avg_b_delta_db <= avg_delta:
        profile_hits += 1
        #print "avg b delta", avg_b_delta_db, avg_delta


    cur.execute("SELECT avg(\"Last B. Delta\") FROM races where \"Class Change\" = %s and Distance=%s and Class=\"%s\"" % (horse.down_class, race_distance,race_class))
    last_b_delta_db = cur.fetchone()[0]
    if not last_b_delta_db:
        cur.execute(
            "SELECT avg(\"Last B. Delta\") FROM races where \"Class Change\" = %s and Class=\"%s\"" % (
            horse.down_class, race_class))
        last_b_delta_db = cur.fetchone()[0]

    if last_b_delta_db <= last_delta:
        profile_hits += 1
        #print "last beyer delta", last_b_delta_db, last_delta

    return profile_hits

def load_winners():

    scrape_codes = {'SA':'santa-anita','GP': 'gulfstream-park','DMR':'del-mar',
    'PRX':'parx-racing','BEL':'belmont-park','KEE':'keeneland','CD':'churchill-downs',
    'FG':'fair-grounds','AQU':'aqueduct','GPW':'gulfstream-park-west','HOU':'sam-houston','LRC':'los-alamitos-race-course',
    'MNR':'mountaineer','TAM':'tampa-bay-downs','OP':'oaklawn-park','PIM':'pimlico-race-course','IN':'indiana-grand',
                    'MTH':'monmouth-park','SAR':'saratoga', 'PEN':'penn-national', 'IND':'indiana-grand'
    }
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    url = "https://entries.horseracingnation.com/entries-results/%s/%s" % (scrape_codes[race_track], race_date.strftime('%Y-%m-%d'))
    req = requests.get(url, headers)
    global winners_dict
    soup = BeautifulSoup(req.content, 'html.parser')
    tables = soup.find_all("table", {"class": "table table-hrn table-payouts"})
    for table in tables:
        tbody = table.find("tbody")
        first_row = tbody.find("tr")
        cells = first_row.findAll("td")
        name = cells[0].get_text().strip()
        post = cells[1].find("img")['title'].strip()
        price = cells[2].get_text().strip()
        winners_dict[name] = {'price': price.strip('$'), 'post': post}

    return winners_dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('race_source')
    parser.add_argument('--results', action='store_true')

    options = parser.parse_args()

    race_short_code = os.path.basename(os.path.normpath(options.race_source))
    with open(options.race_source + '.cr', 'r') as f:
        for row in csv.reader(f):
            global race_date
            race_date = datetime.datetime.strptime(row[1],'%m/%d/%Y')
            global race_track
            race_track = row[0]
            global surface
            surface = row[17]
            race_descriptions[int(row[2])] = 'Race %s: %s \n%s\n%s %s %s' % (row[2], row[4], row[26], row[15], row[11], surface)
            race_surfaces[int(row[2])] = surface
            race_classes[int(row[2])] = class_rankings[row[11]]
            race_distances[int(row[2])] = float(row[15])
            race_purses[int(row[2])] = row[12]
            race_class_code[int(row[2])] = row[11]
            race_claim_prices[int(row[2])] = row[13]
    with open(options.race_source + '.pgh', 'r') as f:
        for row in csv.reader(f):
            morning_lines[row[5]] = row[7]

    if options.results:
        load_winners()
    with open(options.race_source + '.ch', 'r') as f:
        for row in csv.reader(f):
            race_id = int(row[2])
            if race_id not in races:
                races[race_id] = Race(track_code=row[0], race_number=row[2],class_value=race_classes[race_id],
                                      distance=race_distances[race_id], race_class=race_class_code[race_id],
                                      race_purse=race_purses[race_id], race_date=row[1],
                                      surface=race_surfaces[race_id])
            pps = get_pps(row[5])
            special_products = get_special_products(row[5])
            tom_dist = special_products[15].replace("*", "")
            tom_mud = special_products[13].replace("*", "")
            tom_turf = special_products[14].replace("*", "")

            works = get_works(row[5])
            if len(works) > 0:
                (works_rate, had_bullet) = get_works_rate(works[:3])
            else:
                works_rate = 1.0
                had_bullet = False
            if len(pps) > 2:
                if get_form_bonus(pps):
                    form_bonus = True
                else:
                    form_bonus = False
                if get_super_gain(pps):
                    super_gain = True
                else:
                    super_gain = False
                if get_fluke(pps):
                    fluke = True
                else:
                    fluke = False
            else:
                form_bonus = False
                fluke = False
                super_gain = False
            if len(pps) > 0:
                if races[race_id].class_value < class_rankings[pps[0][13]]:
                    down_class = -1
                elif races[race_id].class_value > class_rankings[pps[0][13]]:
                    down_class = 1
                else:
                    down_class = 0
                #if track_abbreviations[races[race_id].track_code] > track_abbreviations[pps[0][7]]:
                #    down_track = True
                #else:
                down_track = False
                max_position = max_class_and_finish(pps)
                if races[race_id].distance > float(pps[0][12]):
                    dist_change = 1
                elif races[race_id].distance < float(pps[0][12]):
                    dist_change = -1
                else:
                    dist_change = 0
                early_rate = get_early_rate(pps)
                max_beyer, max_beyer_days_ago = get_max_beyer(pps[:6])
                avg_beyer = get_avg_beyer(pps[:6])
                pen_rate = get_pen_rate(pps[:6])
                last_beyer = int(pps[0][57])
                last_odds = float(pps[0][62])
                last_odds_pos = int(pps[0][63])
                if len(pps) > 2:  # qualify
                    oods_sum = float(pps[0][62]) + float(pps[1][62]) + float(pps[2][62])
                    avg_odds = (oods_sum / 3)
                else:
                    avg_odds = 0.0
                previous_jockey_name = pps[0][70]
                if last_beyer in [998, 999]:
                    last_beyer = -1
                if pps[0][10] == '-':  # timeform
                    last_beyer -= 14
                chances_rate = get_chances_rate(pps)
                improvement_rate = get_improvement_rate(pps)
                zags = get_zags(pps)
                loss_distance = get_loss_distances(pps)
                closing_speed = get_closing_speed(pps)
                best_result_at_distance = get_best_result_at_distance(pps, races[race_id].distance)
                best_result_at_comp = get_best_result_at_comp(pps, races[race_id].race_class, race_claim_prices[race_id])
                #print pps[0][3]
                #print(best_result_at_comp)
                stars = 0
                if len(pps) > 0:
                    if int(pps[0][52]) == 1:
                        won_last = True
                        stars += 1
                    else:
                        won_last = False
                    stars +=1
                else:
                    won_last = False
                #last_track = '%s %s/%s/%s %s %s' % (pps[0][7], num2words(int(pps[0][52]), to='ordinal_num'), pps[0][57], pps[0][53], pps[0][12], pps[0][14])
                #last_track += '\n %s' % pps[0][60]
                last_track = pps[0][7] + "-" + pps[0][14]
                #last_track = pps[0][7]
                last_date = datetime.datetime.strptime(pps[0][6], '%m/%d/%Y')
                race_date = datetime.datetime.strptime(row[1], '%m/%d/%Y')
                layoff = (race_date - last_date).days
                last_finish = pps[0][52]
                last_finish_distance = pps[0][53]

                if int(pps[0][52]) == 2 or (pps[0][52] != 1 and pps[0][53] <= 2.5):
                    stars += 1




                if int(pps[0][52]) == 1 and pps[0][13] == 'MSW' and float(pps[0][16]) >= 40 and int(row[42]) in [2,3,4,5] and works_rate > -.35:
                    maiden_lock = True
                else:
                    maiden_lock = False
            else:
                max_position = ('','')
                maiden_lock = False
                last_track = ''
                early_rate = -1
                max_beyer = -1
                max_beyer_days_ago = 0
                dist_change = ''
                last_beyer = -1
                avg_beyer = -1
                chances_rate = -1
                improvement_rate = -1
                down_class = 0
                won_last = False
                down_track = False
                zags = 0
                loss_distance = 99
                closing_speed = False
                stars = 0
                best_result_at_distance = -1
                best_result_at_comp = ''
                last_finish = ''
                last_finish_distance = ''
                fluke = False
                layoff = 0
                previous_jockey_name = ''
                pen_rate = 0.0
                last_odds = 0
                last_odds_pos = 0
                avg_odds = 0.0
            if float(row[79]) > 0:
                jockey_second = float(row[82]) / float(row[79])
            else:
                jockey_second = 0
            races[race_id].horses.append(Horse(name=row[5] if row[6] == 'D' else '%s (%s)' % (row[5], row[11]),
                                               early_rate=early_rate,
                                               max_beyer=max_beyer,
                                               max_beyer_days_ago = max_beyer_days_ago,
                                               avg_beyer=avg_beyer,
                                               jockey=row[84],
                                               jockey_second= jockey_second,
                                               chances_rate=chances_rate,
                                               lifetime_starts=int(row[42]),
                                               post=row[30],
                                               morning_line=morning_lines[row[5]],
                                               wins=int(row[43]),
                                               place=int(row[44]),
                                               show=int(row[45]),
                                               improvement_rate=improvement_rate,
                                               form_bonus=form_bonus,
                                               down_class=down_class,
                                               down_track=down_track,
                                               sale=float(row[21]),
                                               trainer_pct=float(row[98]),
                                               fluke=fluke,
                                               won_last=won_last,
                                               last_finish=last_finish,
                                               last_finish_distance=last_finish_distance,
                                               super_gain=super_gain,
                                               zags=zags,
                                               loss_distance=loss_distance,
                                               closing_speed=closing_speed,
                                               last_track=last_track,
                                               works=works_rate,
                                               had_bullet=had_bullet,
                                               last_beyer=last_beyer,
                                               #cur_year_earnings=(float(row[41])*1000) if float(row[41]) > 0 else 0,  # lifetime
                                               cur_year_earnings=(float(row[31])*1000) / float(row[32]) if float(row[32]) > 0 else 0,
                                               stars=stars,
                                               best_result_at_distance=best_result_at_distance,
                                               best_result_at_comp= best_result_at_comp,
                                               jockey_name=row[28],
                                               previous_jockey_name=previous_jockey_name,
                                               maiden_lock=maiden_lock,
                                               tom_dist=tom_dist,
                                               tom_turf=tom_turf,
                                               tom_mud=tom_mud,
                                               layoff=layoff,
                                               max_position=max_position,
                                               dist_change=dist_change,
                                               pen_rate = pen_rate,
                                               last_odds = last_odds,
                                               last_odds_pos = last_odds_pos,
                                               avg_odds = avg_odds
                                               )
                                         )
            if int(row[42]) < 2:
                races[race_id].maiden_trainer_rankings.append(float(row[98]))
                races[race_id].maiden_sale_rankings.append(float(row[21]))
                races[race_id].maiden_works_rankings.append(works_rate)

            races[race_id].trainer_rankings.append(float(row[98]))
            races[race_id].sale_rankings.append(float(row[21]))
            races[race_id].works_rankings.append(works_rate)
            if int(row[43]) > races[race_id].max_wins:
                races[race_id].max_wins = int(row[43])
            races[race_id].last_beyer_rankings.append(last_beyer)
            races[race_id].early_rate_rankings.append(early_rate)
            races[race_id].max_beyer_rankings.append(max_beyer)
            races[race_id].avg_beyer_rankings.append(avg_beyer)
            races[race_id].jockey_rankings.append(row[84])
            races[race_id].chances_rankings.append(chances_rate)
            races[race_id].improvement_rankings.append(improvement_rate)
            races[race_id].loss_distance_rankings.append(loss_distance)
            races[race_id].money_rate_rankings.append( float((int(row[43]) + int(row[44]) + int(row[45]))) / int(row[42]) if int(row[42]) > 0 else 0.0)
            #races[race_id].cur_year_earnings_rankings.append((float(row[41])*1000) if float(row[41]) > 0 else 0.0) # last year

            races[race_id].cur_year_earnings_rankings.append((float(row[31])*1000) / float(row[32]) if float(row[32]) > 0 else 0.0)


    tables = []
    winner_rows = []
    for race in sorted(races.keys()):
        table = []
        maiden_table = []  # one or fewer races
        maidens = sum(1 for x in races[race].horses if x.lifetime_starts < 2)
        for horse in races[race].horses:
            races[race].early_rate_rankings.sort(reverse=True)
            races[race].jockey_rankings.sort(reverse=True)
            races[race].chances_rankings.sort(reverse=True)
            races[race].max_beyer_rankings.sort(reverse=True)
            races[race].avg_beyer_rankings.sort(reverse=True)
            races[race].last_beyer_rankings.sort(reverse=True)
            races[race].improvement_rankings.sort(reverse=True)
            races[race].loss_distance_rankings.sort()
            races[race].cur_year_earnings_rankings.sort(reverse=True)
            races[race].money_rate_rankings.sort(reverse=True)
            races[race].works_rankings.sort(reverse=True)
            races[race].trainer_rankings.sort(reverse=True)
            races[race].sale_rankings.sort(reverse=True)
            races[race].maiden_works_rankings.sort(reverse=True)
            races[race].maiden_trainer_rankings.sort(reverse=True)
            races[race].maiden_sale_rankings.sort(reverse=True)

            if races[race].avg_beyer_rankings[0] - 3 <= horse.avg_beyer:  # within 3
                horse.stars += 1

            if Ranking(races[race].cur_year_earnings_rankings, start=1, strategy=COMPETITION).rank(horse.cur_year_earnings) <= 2:
                horse.stars += 1

            horse.aggregate += len(races[race].horses)+1 - Ranking(races[race].money_rate_rankings, start=1, strategy=COMPETITION).rank(horse.money_rate)
            if Ranking(races[race].last_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.last_beyer) <= 2:
                horse.stars += 1


            if Ranking(races[race].jockey_rankings, start=1, strategy=COMPETITION).rank(horse.jockey) <= 3:
                horse.stars += 1

            """
            if horse.maiden_lock:
                horse.bonuses.append("MAIDEN LOCK!")
            """
            if horse.down_class < 0:
                horse.bonuses.append("\/")
                horse.stars += 1
                if Ranking(races[race].avg_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.avg_beyer) == 1 and Ranking(races[race].jockey_rankings, start=1, strategy=COMPETITION).rank(horse.jockey) in [1,2]:
                    horse.bonuses.append("LOCK!")

            """
            if horse.form_bonus:
                horse.bonuses.append("Form")
                horse.stars += 1

            if horse.super_gain:
                horse.bonuses.append('SG')
                horse.stars += 1
            """
            if horse.best_result_at_distance == 1:
                horse.stars += 1

            total_possible = sum(range(1,len(races[race].horses)+1))*6
            probability = (horse.aggregate / total_possible) * 100

            #horse.bonuses.append(horse.max_position[0])
            #horse.bonuses.append(horse.max_position[1])

            if horse.lifetime_starts <= 2:
                #horse.bonuses.append("%.2f/%.2f" % (float(horse.trainer_pct)+float(horse.jockey), float(horse.trainer_pct)))
                horse.bonuses.append(horse.tom_dist)
                if races[race].surface == 'T':
                    horse.bonuses.append(horse.tom_turf)

            if horse.fluke and horse.had_bullet:
                    horse.bonuses.append("BB")

            true_ml = float(int(horse.morning_line.split("-")[0])/int(horse.morning_line.split("-")[1]))
            if true_ml >= 10:
                horse.long_shot = True

            if true_ml >= 8 and horse.loss_distance <= 2.0:
                horse.bonuses.append('LD')

            if horse.won_last:
                short_code = horse.last_track.split("-")[0]
                if short_code != races[race].track_code:
                    horse.bonuses.append("DH")





            if true_ml >= 10 and Ranking(races[race].jockey_rankings, start=1, strategy=DENSE).rank(horse.jockey) == 1:
                horse.long_shot = True
            if true_ml >= 10 and Ranking(races[race].early_rate_rankings, start=1, strategy=DENSE).rank(
                    horse.early_rate) == 1:
                horse.long_shot = True
            if true_ml >= 10 and Ranking(races[race].improvement_rankings, start=1, strategy=DENSE).rank(
                    horse.improvement_rate) == 1 and horse.lifetime_starts > 2:
                horse.long_shot = True


            if horse.closing_speed and horse.lifetime_starts <= 3:
                1
                #horse.bonuses.append("CS")


            if horse.zags > 1:
                horse.bonuses.append("Z(%s)" % horse.zags)


            if Ranking(races[race].avg_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.avg_beyer) == 1:
                avg_delta = horse.avg_beyer - races[race].avg_beyer_rankings[1]
            else:
                avg_delta = - (races[race].avg_beyer_rankings[0] - horse.avg_beyer)

            if Ranking(races[race].max_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.max_beyer) == 1:
                max_delta = horse.max_beyer - races[race].max_beyer_rankings[1]
            else:
                max_delta = -(races[race].max_beyer_rankings[0] - horse.max_beyer)

            if Ranking(races[race].last_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.last_beyer) == 1:
                last_delta = horse.last_beyer - races[race].last_beyer_rankings[1]
            else:
                last_delta = -(races[race].last_beyer_rankings[0] - horse.last_beyer)


            if Ranking(races[race].early_rate_rankings, start=1, strategy=COMPETITION).rank(horse.early_rate) == 1:
                try:
                    second = next(x for x in races[race].early_rate_rankings if x < races[race].early_rate_rankings[0])
                except:
                    second = 0
                early_delta = horse.early_rate - second
            else:
                early_delta = -(races[race].early_rate_rankings[0] - horse.early_rate)

            horse.stars = profile_horse(horse, races[race].race_class,races[race].distance, avg_delta, max_delta, last_delta)

            if horse.max_beyer == horse.last_beyer and horse.down_class in [0,1] and horse.lifetime_starts >= 3:
                horse.bonuses.append("Po.")

            if horse.long_shot:
                value_town = 0
                if float(horse.jockey) >= .15:
                    value_town += 1
                if float(horse.trainer_pct) >= .15:
                    value_town += 1
                if float(horse.works) >= -.45 and float(horse.works) != 0:
                    value_town += 1
                if max_delta >= -10:
                    value_town +=1
                if last_delta >= -16:
                    value_town += 1
                if horse.wins == races[race].max_wins and horse.wins > 2:
                    value_town += 1
                    horse.bonuses.append("Max W's")

                if value_town >= 3:
                    horse.bonuses.append("Value Town: %s" % value_town)



            if Ranking(races[race].max_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.max_beyer) in [1,2] and horse.down_class == -1:
                horse.bonuses.append("Me likey")



            header_row = ['Date','Track','Race','Class','Distance','Surface','Price','Horse','Lifetime Starts',
                          'Wins','Place','Show','Avg. B. Ranking','Avg. B. Delta','Last B. Ranking','Last B. Delta',
                          'Max B. Ranking', 'Max B. Delta','Jockey Ranking', 'Jockey', 'Early Ranking', 'Early',
                          'Trainer Ranking', 'Trainer', 'Work Ranking', 'Works', 'Year Earnings Rankings', 'Year Earnings',
                          'Form', 'Super Gain', 'Class Change','Dist Change','Won Last', 'Last Finish','Last Finish Distance', 'Had Bullet',
                          'Fluke','Tom Dist','Tom Turf', 'Tom Mud','Layoff']
            if options.results and horse.name in winners_dict:
                horse_row = []
                horse_row.append(race_date.strftime("%Y/%m/%d"))
                horse_row.append(race_track)
                horse_row.append(races[race].race_number)
                horse_row.append(races[race].race_class)
                horse_row.append(races[race].distance)
                horse_row.append(races[race].surface)
                horse_row.append(winners_dict[horse.name]['price'])
                horse_row.append(horse.name)
                horse_row.append(horse.lifetime_starts)
                horse_row.append(horse.wins) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.place) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.show) if horse.lifetime_starts > 0 else horse_row.append('')
                ##
                horse_row.append(Ranking(races[race].avg_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.avg_beyer))
                horse_row.append(avg_delta) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(Ranking(races[race].last_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.last_beyer))
                horse_row.append(last_delta) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(Ranking(races[race].max_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.max_beyer))
                horse_row.append(max_delta) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(Ranking(races[race].jockey_rankings, start=1, strategy=COMPETITION).rank(horse.jockey))
                horse_row.append(horse.jockey)
                horse_row.append(Ranking(races[race].early_rate_rankings, start=1, strategy=COMPETITION).rank(horse.early_rate)) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.early_rate) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(Ranking(races[race].trainer_rankings, start=1, strategy=COMPETITION).rank(horse.trainer_pct))
                horse_row.append(horse.trainer_pct)
                horse_row.append(Ranking(races[race].works_rankings, start=1, strategy=COMPETITION).rank(horse.works))
                horse_row.append('%.2f' % horse.works) if horse.works < 0 else horse_row.append('')
                horse_row.append(Ranking(races[race].cur_year_earnings_rankings, start=1, strategy=COMPETITION).rank(horse.cur_year_earnings))
                horse_row.append(horse.cur_year_earnings) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.form_bonus) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.super_gain) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.down_class) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.dist_change) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.won_last) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.last_finish) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.last_finish_distance) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.had_bullet)
                horse_row.append(fluke) if horse.lifetime_starts > 0 else horse_row.append('')
                horse_row.append(horse.tom_dist)
                horse_row.append(horse.tom_turf)
                horse_row.append(horse.tom_mud)
                horse_row.append(horse.layoff) if horse.layoff else horse_row.append('')


                with open('eggs.csv', 'a') as f:
                    spamwriter = csv.writer(f)
                    spamwriter.writerow(horse_row)
                    #spamwriter.writerow(header_row)
                    #exit(1)
                    #return
                break

            table.append([
                    #'%s %s %s %s %s' % (races[race].race_date,races[race].track_code,races[race].race_number,
                    #              races[race].race_class, races[race].race_purse),
                    horse.stars * '*',
                    '%s (%s) \n%s'  % (horse.name, horse.post, horse.morning_line),
                              '%s:%s-%s-%s' % (horse.lifetime_starts, horse.wins, horse.place, horse.show),
                              '%s %s %s' % (horse.avg_beyer, num2words(Ranking(races[race].avg_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.avg_beyer), to='ordinal_num'), avg_delta),
                              '%s %s %s' % (horse.last_beyer, num2words(Ranking(races[race].last_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.last_beyer), to='ordinal_num'), last_delta),
                              '%s %s %s %s' % (horse.max_beyer,horse.max_beyer_days_ago, num2words(Ranking(races[race].max_beyer_rankings, start=1, strategy=COMPETITION).rank(horse.max_beyer), to='ordinal_num'), max_delta),
                              '%s %s %s%s' % (horse.jockey,Ranking(races[race].jockey_rankings, start=1, strategy=DENSE).rank(horse.jockey), horse.jockey_name[:3], '/' + horse.previous_jockey_name[:2] if len(horse.previous_jockey_name) > 0 else ''),
                              '%.2f' % horse.trainer_pct,
                              '%.2f %s' % (horse.works, '*' if horse.had_bullet else ''),
                              '%.2f %s' % (horse.early_rate if horse.lifetime_starts >= 2 else 0.0, (str("%.2f" % early_delta) if early_delta > 0 else '') if horse.lifetime_starts >= 2 else ''),
                              '%.2f' % (horse.improvement_rate if horse.lifetime_starts >= 2 else 0.0),
                              '%.2f' % horse.pen_rate,
                              '%s %s' % (locale.currency(horse.cur_year_earnings / 1000, symbol=True, grouping=True), Ranking(races[race].cur_year_earnings_rankings, start=1, strategy=COMPETITION).rank(horse.cur_year_earnings)),
                              '%s' % horse.form_bonus,
                              '%s' % horse.super_gain,
                              '%s' % horse.down_class,
                              '%s' % horse.last_track,
                              '%s' % horse.last_finish,
                              '%s' % horse.last_finish_distance,
                              '%.1f\n%s' % (horse.last_odds, '(' + num2words(horse.last_odds_pos, to='ordinal_num') + ')' if horse.last_odds_pos > 0 else ''), # num2words(pp[52],to='ordinal_num'
                              '%.1f' % horse.avg_odds,
                              '%s' % horse.layoff,

                ' '.join(map(str, horse.bonuses)),
                              ])
        table.sort(key=lambda x:(x[0], x[3]), reverse=True)
        tables.append((table,maiden_table))
    #with open('/Users/dcoleyoung/Desktop/winner_files/%s_picks.csv' % race_short_code, "w") as myfile:
    #    myfile.write(race_short_code)
    #    myfile.write("\n")
    if not options.results:
        for index, table_tuple in enumerate(tables):
            print(race_descriptions[index + 1])
            print tabulate(table_tuple[0],
                           tablefmt="pretty",
                           headers=["Rating", "Name","Life", "Avg\nBeyer","Last\nBeyer","Max\nBeyer", "Jockey","Tr.",
                                    "Works","Early","Late","Pen Call","$","Form","SG","Class","Last Track","LF","LFD",
                                    "Last Odds","Avg Odds","Layoff","Bonuses","Comp"])


if __name__ == "__main__":
    main()
