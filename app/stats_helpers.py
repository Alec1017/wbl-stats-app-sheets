def calc_hits(singles, doubles, triples, home_runs):
    return singles + doubles + triples + home_runs


def calc_at_bats(hits, outs, strikeouts):
    return hits + outs + strikeouts


def calc_obp(hits, at_bats, base_on_balls, hit_by_pitch):
    denom = at_bats + base_on_balls + hit_by_pitch
    if denom == 0:
        return 'Undefined'

    return round(float((hits + base_on_balls + hit_by_pitch) / denom), 3)


def calc_avg(hits, at_bats):
    if at_bats == 0:
        return 'Undefined'

    return round(float(hits / at_bats), 3)


def calc_slg(singles, doubles, triples, home_runs, at_bats):
    if at_bats == 0:
        return 'Undefined'

    return round(float((singles + (2 * doubles) + (3 * triples) + (4 * home_runs)) / at_bats), 3)


def calc_ops(obp, slg):
    if obp == 'Undefined' or slg == 'Undefined':
      return 'Undefined'

    return round(float(obp + slg), 3) if obp + slg != 0 else 'Undefined'


def calc_era(earned_runs, innings_pitched):
    if innings_pitched == 0:
        return 'Undefined'

    return round(float((earned_runs * 3) / innings_pitched), 2)


def calc_innings_pitched(outsPitched):
    return round(float(outsPitched / 3.0), 2)