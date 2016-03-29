# -*- coding: utf-8 -*-

from decimal import Decimal
from functools import reduce
from logging import getLogger

from . import config, utils


logger = getLogger('app.decision')


def build_decision_matrix(params_list):
    """ Creates decision matrix data structure.

    Matches passed in parameter and rating tuple to the respective weighting in DM_WEIGHTINGS.
    Parameters that do not exist in DM_WEIGHTINGS are ignored. Conversely, if no matching tuple is passed in for
    a key in DM_WEIGHTINGS, it will not be included in the final matrix (other parameter weightings will be
    recalculated accordingly).

    :param params_list: list of tuples, (parameter_name, rating)
        - parameter_name must match a key in DM_WEIGHTINGS
    :return: decision matrix, dictionary of the form { parameter: (weight, rating), ... }
    """
    matrix = {}
    total_weight = Decimal(0)
    for parameter, rating in params_list:
        weight = config.DM_WEIGHTINGS.get(parameter)
        if weight is not None:
            matrix[parameter] = (weight, rating)
            total_weight += weight
        logger.debug('parameter {0} has weight {1} and rating {2}'.format(parameter, weight, rating))

    # if there are missing parameter ratings, recalculate weightings
    if len(matrix) != len(config.DM_WEIGHTINGS):
        for key, value in matrix.items():
            weight, rating = value
            matrix[key] = (weight/total_weight, rating)
            logger.debug('parameter {0} has recalculated weight, rating {1}'.format(key, matrix[key]))

    return matrix


def evaluate_decision_matrix(matrix):
    """ Evaluates decision matrix.

    Calculates the total score based on weighting and rating of each parameter.
    Determines new thermostat state based on total score and preset thresholds.

    Normalizes ratings to be within range(-1, 1) before multiplying weight.

    :param matrix: decision matrix
    :return: new thermostat state
    """
    total_score = Decimal(0)
    total_rating = reduce(lambda x, y: x+y, [value[1] for value in matrix.values()])

    for key, value in matrix.items():
        score = reduce(lambda weight, rating: weight*(rating/total_rating), value)
        total_score += score
    total_score *= config.SCORE_MODIFIER
    logger.debug('total rating is {0}'.format(total_rating))
    logger.debug('total score is {0}'.format(total_score))

    new_state = utils.State.IDLE
    if total_score > config.DM_HEAT_THRESHOLD:
        new_state = utils.State.HEAT
    elif total_score < config.DM_COOL_THRESHOLD:
        new_state = utils.State.COOL

    return new_state
