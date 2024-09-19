from __future__ import print_function
import csv
import datetime
from tabulate import tabulate
import sys
from ranking import Ranking, COMPETITION
import sqlite3
import argparse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Global dictionaries for signals
favorite_signals = {}
mid_price_signals = {}
longshot_signals = {}

class Race:
    def __init__(self, track_code, race_number, class_value, distance, race_class, race_purse, race_date, surface, description):
        self.track_code = track_code
        self.race_number = race_number
        self.class_value = class_value
        self.distance = distance
        self.race_class = race_class
        self.race_purse = race_purse
        self.race_date = race_date
        self.surface = surface
        self.horses = []
        self.early_rate_rankings = []
        self.description = description

class Horse:
    def __init__(self, name='', post='', morning_line='', bet_number='', jockey='', jockey_pct=0.0, trainer='', trainer_pct=0.0, jockey_trainer_pct=0.0, wins=0, place=0, show=0, lifetime_starts=0, last_track='', last_odds=0.0, last_finish='', was_favorite=False, country='', tomlinson_turf=0, tomlinson_dist=0, tomlinson_mud=0, layoff=0):
        self.name = name
        self.post = post
        self.morning_line = morning_line
        self.bet_number = bet_number
        self.jockey = jockey
        self.jockey_pct = jockey_pct
        self.trainer = trainer
        self.trainer_pct = trainer_pct
        self.jockey_trainer_pct = jockey_trainer_pct
        self.wins = wins
        self.place = place
        self.show = show
        self.lifetime_starts = lifetime_starts
        self.early_rate = 0.0
        self.early_rank = 0
        self.avg_beyer = 0
        self.avg_beyer_rank = 0
        self.avg_beyer_delta = 0
        self.last_beyer = 0
        self.last_beyer_rank = 0
        self.last_beyer_delta = 0
        self.max_beyer = 0
        self.max_beyer_rank = 0
        self.max_beyer_delta = 0
        self.last_track = last_track
        self.last_odds = last_odds
        self.last_finish = last_finish
        self.was_favorite = was_favorite
        self.country = country
        self.longshot_criteria = []
        self.tomlinson_turf = tomlinson_turf
        self.tomlinson_dist = tomlinson_dist
        self.tomlinson_mud = tomlinson_mud
        self.layoff = layoff
    def get_truncated_name(self, max_length=20):
        if len(self.name) <= max_length:
            return self.name
        return self.name[:max_length-3] + '...'

def load_race_data(filename):
    races = {}
    with open(filename + '.cr', 'r') as f:
        for row in csv.reader(f):
            race_id = int(row[2])
            race_description = 'Race {0}: {1} \n{2}\n{3} {4} {5} {6}'.format(
                row[2],  # race number
                row[4],  # race name
                row[26],  # conditions
                row[15],  # distance
                row[11],  # class
                row[17],  # surface
                '\n' + beyer_priorities[row[11]] if row[11] in beyer_priorities else ''
            )
            races[race_id] = Race(
                track_code=row[0],
                race_number=row[2],
                class_value=row[11],
                distance=float(row[15]),
                race_class=row[11],
                race_purse=row[12],
                race_date=datetime.datetime.strptime(row[1], '%m/%d/%Y'),
                surface=row[17],
                description=race_description
            )
    return races

# Add this at the top of your file with other imports
beyer_priorities = {
    'G1': 'Beyer Priority: Max',
    'G2': 'Beyer Priority: Max',
    'G3': 'Beyer Priority: Max',
    'N': 'Beyer Priority: Max',
    'A': 'Beyer Priority: Max',
    'R': 'Beyer Priority: Avg',
    'B': 'Beyer Priority: Avg',
    'C': 'Beyer Priority: Last',
    'S': 'Beyer Priority: Last'
}

def custom_rank(values, reverse=False):
    sorted_values = sorted(set(values), reverse=reverse)
    return {value: rank for rank, value in enumerate(sorted_values, 1)}

def load_horse_data(filename, races):
    morning_lines = {}
    bet_numbers = {}

    # Load morning lines and bet numbers from .pgh file
    with open(filename + '.pgh', 'r') as f:
        for row in csv.reader(f):
            morning_lines[row[5]] = row[7]
            bet_numbers[row[5]] = row[3]

    # Load horse data from .ch file and assign morning lines and bet numbers
    for race in races.values():
        race.early_rate_rankings = []
        race.avg_beyer_rankings = []
        race.last_beyer_rankings = []
        race.max_beyer_rankings = []

    with open(filename + '.ch', 'r') as f:
        for row in csv.reader(f):
            race_id = int(row[2])
            horse_name = row[5]
            # Add AE or MTO indicator to the post number
            mto_ae = row[3]
            post = row[30]
            if mto_ae == 'A':
                post += ' (AE)'
            elif mto_ae == 'M':
                post += ' (MTO)'

            pps = get_pps(horse_name, filename)
            last_track, last_odds, last_finish, was_favorite, layoff = get_last_track(pps, races[race_id].race_date)

            special_products = get_special_products(horse_name)
            tom_dist = special_products[15].replace("*", "")
            tom_mud = special_products[13].replace("*", "")
            tom_turf = special_products[14].replace("*", "")

            horse = Horse(
                name=row[5] if row[6] == 'D' else '%s (%s)' % (row[5], row[11]),
                post=post,  # Use the modified post number
                morning_line=morning_lines.get(horse_name, 'Unknown'),
                bet_number=bet_numbers.get(horse_name, 'Unknown'),
                jockey=row[28],
                jockey_pct=float(row[84]),
                trainer=row[29],
                trainer_pct=float(row[98]),
                jockey_trainer_pct=float(row[116]),
                wins=int(row[43]),
                place=int(row[44]),
                show=int(row[45]),
                lifetime_starts=int(row[42]),
                last_track=last_track,
                last_odds=last_odds,
                last_finish=last_finish,
                was_favorite=was_favorite,
                country=row[11],
                tomlinson_turf=tom_turf,
                tomlinson_dist=tom_dist,
                tomlinson_mud=tom_mud,
                layoff=layoff  # Add the layoff attribute here
            )

            # Calculate early rate
            horse.early_rate = get_early_rate(pps)
            horse.avg_beyer = get_avg_beyer(pps)
            horse.last_beyer = get_last_beyer(pps)
            horse.max_beyer = get_max_beyer(pps)

            races[race_id].horses.append(horse)
            races[race_id].early_rate_rankings.append(horse.early_rate)
            if horse.avg_beyer is not None:
                races[race_id].avg_beyer_rankings.append(horse.avg_beyer)
            races[race_id].last_beyer_rankings.append(horse.last_beyer)
            races[race_id].max_beyer_rankings.append(horse.max_beyer)

    # Calculate rankings for each race
    for race in races.values():
        early_ranking = custom_rank(race.early_rate_rankings, reverse=True)
        avg_beyer_ranking = custom_rank([h.avg_beyer for h in race.horses if h.avg_beyer is not None], reverse=True)
        last_beyer_ranking = custom_rank(race.last_beyer_rankings, reverse=True)
        max_beyer_ranking = custom_rank(race.max_beyer_rankings, reverse=True)
        for horse in race.horses:
            horse.early_rank = early_ranking[horse.early_rate]
            horse.avg_beyer_rank = avg_beyer_ranking.get(horse.avg_beyer, "-") if horse.avg_beyer is not None else "-"
            horse.last_beyer_rank = last_beyer_ranking[horse.last_beyer]
            horse.max_beyer_rank = max_beyer_ranking[horse.max_beyer]

        # Calculate deltas
        top_avg_beyer = max(race.avg_beyer_rankings) if race.avg_beyer_rankings else None
        top_last_beyer = max(race.last_beyer_rankings)
        top_max_beyer = max(race.max_beyer_rankings)
        for horse in race.horses:
            if horse.avg_beyer is not None and top_avg_beyer is not None:
                horse.avg_beyer_delta = horse.avg_beyer - top_avg_beyer
            else:
                horse.avg_beyer_delta = "-"
            horse.last_beyer_delta = horse.last_beyer - top_last_beyer
            horse.max_beyer_delta = horse.max_beyer - top_max_beyer

def get_odds_category(morning_line):
    try:
        numerator, denominator = map(int, morning_line.split('-'))
        odds = numerator / denominator
        if odds <= 3:
            return "Favorite"
        elif odds <= 9:
            return "Mid-range"
        else:
            return "Longshot"
    except (ValueError, ZeroDivisionError):
        return "Unknown"

def get_early_rate(pps):
    total = 0.0
    for pp in pps:
        if float(pp[47]) <= 2.0 or float(pp[46]) == 1:
            total += 1
    return total / len(pps) if len(pps) > 0 else 0.0

def get_pps(horse_name, filename):
    pps = []
    with open(filename + '.chr', 'r') as f:
        for row in csv.reader(f):
            if horse_name == row[3]:
                pps.append(row)
    return pps[:8]  # Return the last 8 past performances


def get_special_products(horse_name):
    with open(sys.argv[1] + '.cs', 'r') as f:
        for row in csv.reader(f):
            if horse_name == row[3]:
                return row

def get_avg_beyer(pps):
    if len(pps) < 3:
        return None
    average_beyer = 0
    total = 0
    min_beyer = float('inf')
    for pp in pps:
        if int(pp[57]) not in [998, 999, -1]:
            speed_figure = int(pp[57])
            if pp[10] == '-':  # timeform
                speed_figure -= 14
            average_beyer += speed_figure
            total += 1
            min_beyer = min(min_beyer, speed_figure)
    if total > 3:  # have 4 to qualify tossing the lowest
        average_beyer -= min_beyer
        total -= 1
    return average_beyer / total if total > 0 else None

def get_last_beyer(pps):
    if pps:
        last_beyer = int(pps[0][57])
        if last_beyer in [998, 999]:
            last_beyer = -1
        if pps[0][10] == '-':  # timeform
            last_beyer -= 14
        return last_beyer
    return 0

def get_max_beyer(pps):
    max_beyer = 0
    for pp in pps:
        speed_figure = int(pp[57])
        if pp[10] == '-':
            speed_figure -= 14
        if speed_figure > max_beyer and speed_figure not in [998, 999]:
            max_beyer = speed_figure
    return max_beyer

def get_last_track(pps, current_race_date):
    if pps:
        last_track = pps[0][7] + "-" + pps[0][14] + ' (%s %s)' % (pps[0][12], pps[0][9])  # last running line
        last_odds = float(pps[0][62]) if pps[0][62] != '' else 0.0
        last_finish = pps[0][52]
        was_favorite = (int(pps[0][63]) == 1)  # Check if the horse was the favorite (post-time favorite)

        # Calculate layoff
        last_race_date = datetime.datetime.strptime(pps[0][6], '%m/%d/%Y')
        layoff = (current_race_date - last_race_date).days

        return last_track, last_odds, last_finish, was_favorite, layoff
    return '-', 0.0, '-', False, 0  # Return 0 for layoff if no previous races

def get_race_tables(races):
    all_tables = []
    for race_id, race in sorted(races.items()):
        table = []

        # Calculate the average of the 4 highest early values for this particular race
        # Only if the race class is not MOC, MSW, or MCL
        top_4_avg = 0
        if race.race_class not in ['MOC', 'MSW', 'MCL']:
            top_4_avg = sum(sorted([horse.early_rate for horse in race.horses], reverse=True)[:4]) / 4 if len(race.horses) >= 4 else 0

        # Group horses by odds category
        favorites = []
        mid_range = []
        longshots = []

        for horse in sorted(race.horses, key=lambda h: float(h.morning_line.split('-')[0])/float(h.morning_line.split('-')[1]) if '-' in h.morning_line else float('inf')):
            category = get_odds_category(horse.morning_line)
            if horse.lifetime_starts == 0:
                last_beyer_info = "-"
                max_beyer_info = "-"
                last_stats = "-"
                max_stats = "-"
                longshot_criteria = "-"
            else:
                # Adjust last_beyer_delta for rank 1
                if horse.last_beyer_rank == 1:
                    second_highest_last_beyer = sorted(race.last_beyer_rankings, reverse=True)[1] if len(race.last_beyer_rankings) > 1 else horse.last_beyer
                    last_beyer_delta = "+{}".format(horse.last_beyer - second_highest_last_beyer)
                    horse.last_beyer_delta = last_beyer_delta
                else:
                    last_beyer_delta = str(horse.last_beyer_delta)

                # Adjust max_beyer_delta for rank 1
                if horse.max_beyer_rank == 1:
                    second_highest_max_beyer = sorted(race.max_beyer_rankings, reverse=True)[1] if len(race.max_beyer_rankings) > 1 else horse.max_beyer
                    max_beyer_delta = "+{}".format(horse.max_beyer - second_highest_max_beyer)
                    horse.max_beyer_delta = max_beyer_delta
                else:
                    max_beyer_delta = str(horse.max_beyer_delta)

                # Add '**' if last Beyer equals max Beyer and horse has at least 3 starts
                last_beyer_star = '**' if horse.last_beyer == horse.max_beyer and horse.lifetime_starts >= 3 else ''
                last_beyer_info = "{}{} ({}) {}".format(horse.last_beyer, last_beyer_star, horse.last_beyer_rank, last_beyer_delta)
                max_beyer_info = "{} ({}) {}".format(horse.max_beyer, horse.max_beyer_rank, max_beyer_delta)

                last_stats = query_race_stats(race.race_class, horse.last_beyer_delta, "Last")
                max_stats = query_race_stats(race.race_class, horse.max_beyer_delta, "Max")

            # Create lifetime stats string with lifetime starts first
            lifetime_stats = "{0}:{1}-{2}-{3}".format(horse.lifetime_starts, horse.wins, horse.place, horse.show)

            last_track_info = "{} ({}d)".format(horse.last_track, horse.layoff) if horse.last_track != '-' else '-'
            if horse.last_track == '-':
                last_odds_finish = '-'
            else:
                last_odds_finish = "{:.1f}{} {}".format(horse.last_odds, '*' if horse.was_favorite else '', horse.last_finish)

            # Swap order of Bet# and Post#, put Post# in parentheses if different
            bet_post = horse.bet_number
            post_number = horse.post.split()[0]  # Get the actual post number without AE/MTO
            if horse.bet_number != post_number:
                bet_post += " ({})".format(post_number)

            # Add AE or MTO indicator if present
            if ' (AE)' in horse.post:
                bet_post += ' (AE)'
            elif ' (MTO)' in horse.post:
                bet_post += ' (MTO)'

            # Check for longshot criteria
            if category == "Longshot":
                horse_data = {
                    'Class': race.race_class,
                    'Lifetime Starts': horse.lifetime_starts,
                    'Distance': race.distance,
                    'Early': horse.early_rate,
                    'Early Ranking': horse.early_rank,
                    'Last B. Ranking': horse.last_beyer_rank,
                    'Avg. B. Ranking': horse.avg_beyer_rank,
                    'Class Change': horse.class_change if hasattr(horse, 'class_change') else '0',
                    'Layoff': horse.layoff if hasattr(horse, 'layoff') else 0,
                    'Trainer Ranking': horse.trainer_rank if hasattr(horse, 'trainer_rank') else 1,
                    'Had Bullet': horse.had_bullet if hasattr(horse, 'had_bullet') else False,
                    'ML Odds': float(horse.morning_line.split('-')[0])/float(horse.morning_line.split('-')[1]),
                    'Wins': horse.wins,
                    'Place': horse.place,
                    'Show': horse.show,
                    'Jockey Ranking': horse.jockey_rank if hasattr(horse, 'jockey_rank') else 1,
                }
                horse.longshot_criteria = is_potential_longshot(horse_data)
            elif category == "Favorite":
                horse_data = {
                    'Class': race.race_class,
                    'Lifetime Starts': horse.lifetime_starts,
                    'Distance': race.distance,
                    'Early': horse.early_rate,
                    'Early Ranking': horse.early_rank,
                    'Last B. Ranking': horse.last_beyer_rank,
                    'Max B. Ranking': horse.max_beyer_rank,
                    'Avg. B. Ranking': horse.avg_beyer_rank,
                    'Class Change': horse.class_change if hasattr(horse, 'class_change') else '0',
                    'Layoff': horse.layoff if hasattr(horse, 'layoff') else 0,
                    'Trainer': horse.trainer_pct,
                    'Had Bullet': horse.had_bullet if hasattr(horse, 'had_bullet') else False,
                    'ML Odds': float(horse.morning_line.split('-')[0])/float(horse.morning_line.split('-')[1]),
                    'Wins': horse.wins,
                    'Place': horse.place,
                    'Show': horse.show,
                    'Jockey': horse.jockey_pct,
                    'Surface': race.surface,
                    'Won Last': horse.last_finish == '1' if hasattr(horse, 'last_finish') else False,
                }
                horse.longshot_criteria = identify_potential_short_price_winner(horse_data)

                horse.longshot_criteria += identify_vulnerable_favorite(horse_data)

            if race.race_class in ['MSW', 'MCL', 'MOC'] and horse.lifetime_starts <= 3:
                if hasattr(horse, 'tomlinson_turf'):
                    horse.longshot_criteria.append("T-{}".format(horse.tomlinson_turf))
                if hasattr(horse, 'tomlinson_dist'):
                    horse.longshot_criteria.append("D-{}".format(horse.tomlinson_dist))


            longshot_info = "\n".join(horse.longshot_criteria) if horse.longshot_criteria else "-"

            row = [
                bet_post,  # Swapped and consolidated bet and post number
                horse.get_truncated_name(),  # Use truncated name
                lifetime_stats,
                "{:.2f} {}".format(horse.jockey_pct, horse.jockey),
                "{:.2f} {}".format(horse.trainer_pct, horse.trainer),
                "{:.2f}".format(horse.jockey_trainer_pct),
                horse.morning_line,
                category,
                "{:.2f} ({})".format(horse.early_rate, horse.early_rank),
                last_track_info,
                last_odds_finish,
                last_beyer_info,
                max_beyer_info,
                last_stats,
                max_stats
            ]

            # Include avg_beyer data only if the race class is not MCL, MOC, or MSW
            if race.race_class not in ['MCL', 'MOC', 'MSW']:
                if horse.lifetime_starts == 0 or horse.avg_beyer is None:
                    avg_beyer_info = "-"
                    avg_stats = "-"
                else:
                    avg_stats = query_race_stats(race.race_class, horse.avg_beyer_delta, "Avg")
                    if horse.avg_beyer_rank == 1:
                        second_highest_avg_beyer = sorted(race.avg_beyer_rankings, reverse=True)[1] if len(race.avg_beyer_rankings) > 1 else horse.avg_beyer
                        avg_beyer_delta = "+{}".format(horse.avg_beyer - second_highest_avg_beyer)
                    else:
                        avg_beyer_delta = str(horse.avg_beyer_delta)
                    avg_beyer_info = "{} ({}) {}".format(horse.avg_beyer, horse.avg_beyer_rank, avg_beyer_delta)

                row.insert(12, avg_beyer_info)
                row.insert(15, avg_stats)

            # Add longshot criteria as the last column
            row.append(longshot_info)

            if category == "Favorite":
                favorites.append(row)
            elif category == "Mid-range":
                mid_range.append(row)
            else:
                longshots.append(row)

        # Add rows to table with dividers
        if favorites:
            table.extend(favorites)
            table.append(["-" * 10] * len(row))  # Divider row
        if mid_range:
            table.extend(mid_range)
            table.append(["-" * 10] * len(row))  # Divider row
        if longshots:
            table.extend(longshots)

        # Adjust the "Early" header based on the race class
        early_header = "Early ({:.2f})".format(top_4_avg) if race.race_class not in ['MOC', 'MSW', 'MCL'] else "Early"

        headers = ["Bet#/Post#", "Name", "Lifetime", "Jockey% Name", "Trainer% Name", "J-T%", "M/L", "Category", early_header, "Last Track", "Last Odds/Finish", "Last Beyer (Rank) Delta", "Max Beyer (Rank) Delta", "Last Win %", "Max Win %"]
        if race.race_class not in ['MCL', 'MOC', 'MSW']:
            headers.insert(12, "Avg Beyer (Rank) Delta")
            headers.insert(15, "Avg Win %")

        headers.append("Longshot Criteria")

        all_tables.append((race.description, headers, table))

    return all_tables

def is_potential_longshot(horse_data):
    criteria_met = []

    # 1. Low Early Speed in Longer Races
    if (float(horse_data['Distance']) >= 8.0 and
        float(horse_data['Early']) < 0.5 and
        int(horse_data['Early Ranking']) > 5):
        criteria_met.append("Closer in longer race")

    # 2. Layoff Returner in Sprints
    if (float(horse_data['Distance']) <= 7.0 and
        int(horse_data['Layoff']) > 30):
        criteria_met.append("Layoff returner in sprint")

    # 3. Low Trainer Ranking with Bullet Work
    if (int(horse_data['Trainer Ranking']) > 10 and
        horse_data['Had Bullet'] == 'True'):
        criteria_met.append("Low-ranked trainer with bullet work")

    # 4. Consistent But Non-Winning
    if (int(horse_data['Lifetime Starts']) > 5 and
        int(horse_data['Wins']) < int(horse_data['Lifetime Starts']) / 5 and
        (int(horse_data['Place']) + int(horse_data['Show'])) > int(horse_data['Lifetime Starts']) / 3):
        criteria_met.append("Consistent in-the-money finisher with few wins")

    return criteria_met

def identify_potential_short_price_winner(horse_data):
    criteria_met = []
    """
    # Class check
    if horse_data['Class'] in ['GStk', 'STK', 'MSW', 'AOC', 'ALW']:
        criteria_met.append("High-class race: {0}".format(horse_data['Class']))

    # Beyer figure check
    try:
        if float(horse_data['Avg. B. Ranking']) <= 2:
            criteria_met.append("Strong Avg Beyer Ranking: {0}".format(horse_data['Avg. B. Ranking']))
        if float(horse_data['Last B. Ranking']) == 1:
            criteria_met.append("Top Last Beyer Ranking")
        if float(horse_data['Max B. Ranking']) == 1:
            criteria_met.append("Top Max Beyer Ranking")
    except ValueError:
        pass  # Skip if ranking is not a valid float
    """

    # Jockey and Trainer check
    try:
        if float(horse_data['Jockey']) >= 0.15:
            criteria_met.append("Strong Jockey (Win %: {0:.2%})".format(float(horse_data['Jockey'])))
        if float(horse_data['Trainer']) >= 0.15:
            criteria_met.append("Strong Trainer (Win %: {0:.2%})".format(float(horse_data['Trainer'])))
    except ValueError:
        pass  # Skip if value is not a valid float

    # Early speed check
    if float(horse_data['Early']) >= 0.7:
        criteria_met.append("Good Early Speed: {0}".format(horse_data['Early']))

    # Win percentage check
    lifetime_starts = int(horse_data['Lifetime Starts'])
    wins = int(horse_data['Wins'])
    if lifetime_starts > 0:
        win_percentage = float(wins) / lifetime_starts
        if win_percentage >= 0.3:
            criteria_met.append("Strong Win Percentage: {0:.2%}".format(win_percentage))

    # Distance check
    if 6 <= float(horse_data['Distance']) <= 8:
        criteria_met.append("Optimal Distance: {0} furlongs".format(horse_data['Distance']))

    # Recent performance check
    if horse_data['Won Last'] == 'True':
        criteria_met.append("Won Last Race")

    return criteria_met

def identify_vulnerable_favorite(horse_data):
    vulnerabilities = []

    """
    # Class check
    if horse_data['Class'] in ['MCL', 'CLM', 'MSW']:
        vulnerabilities.append("Lower-class race: {0}".format(horse_data['Class']))

    # Beyer figure check
    try:
        if float(horse_data['Avg. B. Ranking']) > 2:
            vulnerabilities.append("Weak Avg Beyer Ranking: {0}".format(horse_data['Avg. B. Ranking']))
        if float(horse_data['Last B. Ranking']) > 2:
            vulnerabilities.append("Weak Last Beyer Ranking: {0}".format(horse_data['Last B. Ranking']))
        if float(horse_data['Max B. Ranking']) > 1:
            vulnerabilities.append("Not Top Max Beyer Ranking: {0}".format(horse_data['Max B. Ranking']))
    except ValueError:
        pass  # Skip if ranking is not a valid float
    """

    # Jockey and Trainer check
    try:
        if float(horse_data['Jockey']) < 0.15:
            vulnerabilities.append("Weak Jockey (Win %: {0:.2%})".format(float(horse_data['Jockey'])))
        if float(horse_data['Trainer']) < 0.15:
            vulnerabilities.append("Weak Trainer (Win %: {0:.2%})".format(float(horse_data['Trainer'])))
    except ValueError:
        pass  # Skip if value is not a valid float

    # Early speed check
    if float(horse_data['Early']) < 0.5:
        vulnerabilities.append("Poor Early Speed: {0}".format(horse_data['Early']))

    # Win percentage check
    if horse_data['Class'] not in ['MCL', 'MOC', 'MSW']:
        lifetime_starts = int(horse_data['Lifetime Starts'])
        wins = int(horse_data['Wins'])
        if lifetime_starts > 0:
            win_percentage = float(wins) / lifetime_starts
            if win_percentage < 0.2:
                vulnerabilities.append("Low Win Percentage: {0:.2%}".format(win_percentage))


    # Distance check
    if float(horse_data['Distance']) < 6 or float(horse_data['Distance']) > 8:
        vulnerabilities.append("Non-optimal Distance: {0} furlongs".format(horse_data['Distance']))

    # Layoff check
    if int(horse_data['Layoff']) > 60:
        vulnerabilities.append("Long Layoff: {0} days".format(horse_data['Layoff']))

    return vulnerabilities

def query_race_stats(race_class, beyer_delta, beyer_type):
    conn = sqlite3.connect('races_v2.db')  # Make sure this database file exists
    cur = conn.cursor()

    if beyer_type == "Avg":
        query = """
        SELECT COUNT(*) FROM races_v2
        WHERE class = ? AND "Won Race" = "True"
        AND "Avg. B. Delta" <= ?
        """
    else:
        query = """
        SELECT COUNT(*) FROM races_v2
        WHERE class = ? AND "Won Race" = "True"
        AND "{0} B. Delta" <= ?
        """.format(beyer_type)

    cur.execute(query, (race_class, beyer_delta))
    winning_count = cur.fetchone()[0]

    # This query was incorrect. Let's fix it to count all races of the given class
    query = """
    SELECT COUNT(*) FROM races_v2
    WHERE class = ? AND "Won Race" = "True"
    """
    cur.execute(query, (race_class,))
    total_count = cur.fetchone()[0]

    conn.close()

    if total_count > 0:
        percentage = (float(winning_count) / total_count) * 100
        return "{:.2f}% ({}/{})".format(percentage, winning_count, total_count)
    else:
        return "No data"

def generate_pdf(filename, tables):
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter), leftMargin=3, rightMargin=3, topMargin=5, bottomMargin=5)
    elements = []
    styles = getSampleStyleSheet()

    # Create a custom style for table cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=6,  # Increased from 5 to 6
        leading=7,   # Increased from 6 to 7
        alignment=TA_CENTER
    )

    # Create a custom style for table cells with left alignment for longshot criteria
    cell_style_left = ParagraphStyle(
        'CellStyleLeft',
        parent=styles['Normal'],
        fontSize=6,  # Increased from 5 to 6
        leading=7,   # Increased from 6 to 7
        alignment=TA_LEFT,
        wordWrap='CJK'  # Enable word wrapping
    )

    for race_description, headers, table in tables:
        # Create a list to hold elements for this race
        race_elements = []

        # Add race description
        race_elements.append(Paragraph(race_description, ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=9)))
        race_elements.append(Spacer(1, 3))

        # Calculate column widths
        page_width = landscape(letter)[0] - doc.leftMargin - doc.rightMargin
        col_widths = [
            page_width * 0.03,  # Bet#/Post#
            page_width * 0.12,  # Name (narrowed from 12% to 11%)
            page_width * 0.05,  # Lifetime
            page_width * 0.06,  # Jockey% Name
            page_width * 0.06,  # Trainer% Name
            page_width * 0.03,  # J-T%
            page_width * 0.03,  # M/L
            page_width * 0.04,  # Category
            page_width * 0.04,  # Early
            page_width * 0.06,  # Last Track
            page_width * 0.04,  # Last Odds/Finish
            page_width * 0.05,  # Last Beyer (Rank) Delta
            page_width * 0.05,  # Max Beyer (Rank) Delta
            page_width * 0.04,  # Last Win %
            page_width * 0.04,  # Max Win %
            page_width * 0.20   # Longshot Criteria (increased from 24% to 27%)
        ]

        # Adjust for Avg Beyer columns if present
        if len(headers) > 16:
            col_widths.insert(12, page_width * 0.05)  # Avg Beyer (Rank) Delta
            col_widths.insert(15, page_width * 0.04)  # Avg Win %
            # Redistribute some width from other columns
            col_widths = [width * 0.95 for width in col_widths]

        # Wrap cell contents in Paragraphs
        wrapped_headers = [Paragraph(header, cell_style) for header in headers]
        wrapped_data = []
        for row in table:
            wrapped_row = [Paragraph(str(cell), cell_style if i < len(row) - 1 else cell_style_left) for i, cell in enumerate(row)]
            wrapped_data.append(wrapped_row)

        # Create the table
        t = Table([wrapped_headers] + wrapped_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),  # Added vertical padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Added vertical padding
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black)
        ])

        # Add conditional formatting for divider rows
        for i, row in enumerate(table):
            if row[0].startswith("-"):
                table_style.add('LINEBELOW', (0, i), (-1, i), 0.5, colors.black)  # Thicker line for dividers
                table_style.add('LINEABOVE', (0, i), (-1, i), 0.5, colors.black)  # Thicker line above dividers

        t.setStyle(table_style)

        # Add the table to the race elements
        race_elements.append(t)

        # Wrap all elements for this race in a KeepTogether
        elements.append(KeepTogether(race_elements))

        # Add a small Spacer instead of a PageBreak after each race
        elements.append(Spacer(1, 6))

    # Build the PDF
    doc.build(elements)

def main():
    parser = argparse.ArgumentParser(description="DRF Reader")
    parser.add_argument("filename", help="Input filename")
    parser.add_argument("--pdf", help="Output PDF filename", default=None)
    args = parser.parse_args()

    races = load_race_data(args.filename)
    load_horse_data(args.filename, races)
    tables = get_race_tables(races)

    if args.pdf:
        generate_pdf(args.pdf, tables)
        print("PDF generated: {}".format(args.pdf))
    else:
        for race_description, headers, table in tables:
            print(race_description)
            print(tabulate(table, headers=headers))
            print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()