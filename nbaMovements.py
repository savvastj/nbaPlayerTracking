import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from scipy.spatial.distance import euclidean


def get_movements_json(event_id, game_id):
    """
    Returns the JSON containing the player movement data from the stats.nba.com
    API

    Parameters
    ----------
    event_id : str
        The ID number for the desired play in a game.

    game_id : str
        The ID number the desired game.
    """
    url = "http://stats.nba.com/stats/locations_getmoments/"\
          "?eventid={event_id}&gameid={game_id}".format(event_id=event_id,
                                                        game_id=game_id)

    # Get the webpage
    response = requests.get(url)
    json = response.json()
    return json


def get_movements_df(event_id, game_id):
    """
    Returns a pandas DataFrame containing the player movement data from the
    stats.nba.com API

    Parameters
    ----------
    event_id : str
        The ID number for the desired play in a game.

    game_id : str
        The ID number the desired game.
    """

    json = get_movements_json(event_id, game_id)

    # A dict containing home players data
    home = json["home"]
    # A dict containig visiting players data
    visitor = json["visitor"]
    # A list containing each moment
    moments = json["moments"]

    # Column labels
    headers = ["team_id", "player_id", "x_loc", "y_loc", "radius", "moment",
               "game_clock", "shot_clock"]

    # Initialize our new list
    player_moments = []

    for moment in moments:
        # For each player/ball in the list found within each moment
        for player in moment[5]:
            # Add additional information to each player/ball
            # This info includes the index of each moment, the game clock
            # and shot clock values for each moment
            player.extend((moments.index(moment), moment[2], moment[3]))
            player_moments.append(player)

    # creates the players list with the home players
    players = home["players"]
    # Then add on the visiting players
    players.extend(visitor["players"])

    # initialize new dictionary
    id_dict = {}

    # Add the values we want
    for player in players:
        id_dict[player['playerid']] = [player["firstname"]+" "+player["lastname"],
                                       player["jersey"]]

    # Add the ball to the id_dict
    id_dict.update({-1: ['ball', np.nan]})

    # create the DataFrame
    df = pd.DataFrame(player_moments, columns=headers)
    df["player_name"] = df.player_id.map(lambda x: id_dict[x][0])
    df["player_jersey"] = df.player_id.map(lambda x: id_dict[x][1])

    return df


def travel_dist(player_locations):
    """
    Returns the distance traveled by a player based on his locations

    Parameters
    ----------
    player_locations : pandas DataFrame
        This should be a pandas DataFrame containing 2 columns.  One column
        should contain the x-axis location values and the other column
        should contain the y-axis location values of a player.
    """
    # SO link:
    # https://stackoverflow.com/questions/13590484/calculating-euclidean-distance-between-consecutive-points-of-an-array-with-numpy
    # get differences of each column
    diff = np.diff(player_locations, axis=0)
    # square the differences and add them,
    # then get the square root of that sum
    dist = np.sqrt((diff ** 2).sum(axis=1))
    # Then return the sum of all the distances
    return dist.sum()


# Function to find the distance between players
# at each moment
def player_dist(player_a, player_b):
    """
    Returns the distance between two players for each moment they are on the
    court.

    Parameters:
    player_a : pandas DataFrame
        This should be a pandas DataFrame containing 2 columns.  One column
        should contain the x-axis location values and the other column
        should contain the y-axis location values of a player.

    player_b : pandas DataFrame
        This should be a pandas DataFrame containing 2 columns.  One column
        should contain the x-axis location values and the other column
        should contain the y-axis location values of a player.
    ----------

    """
    return [euclidean(player_a.iloc[i], player_b.iloc[i])
            for i in range(len(player_a))]


def draw_court(ax=None, color="gray", lw=1, zorder=0):
    """
    Returns a matplotlib Axes object containing a basketball court

    Parameters
    ----------
    ax : matplotlib Axes
        The matplotlib Axes to plot the basketball court on.  If no Axes is
        provided get the current Axes.

    color : str
        The color of the court lines.

    lw : int
        The lineweight of the court lines.

    zorder : int
        The Z-order of the basketball court.
    """

    if ax is None:
        ax = plt.gca()

    # Creates the out of bounds lines around the court
    outer = Rectangle((0, -50), width=94, height=50, color=color,
                      zorder=zorder, fill=False, lw=lw)

    # The left and right basketball hoops
    l_hoop = Circle((5.35, -25), radius=.75, lw=lw, fill=False,
                    color=color, zorder=zorder)
    r_hoop = Circle((88.65, -25), radius=.75, lw=lw, fill=False,
                    color=color, zorder=zorder)

    # Left and right backboards
    l_backboard = Rectangle((4, -28), 0, 6, lw=lw, color=color,
                            zorder=zorder)
    r_backboard = Rectangle((90, -28), 0, 6, lw=lw, color=color,
                            zorder=zorder)

    # Left and right paint areas
    l_outer_box = Rectangle((0, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)
    l_inner_box = Rectangle((0, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)
    r_outer_box = Rectangle((75, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)

    r_inner_box = Rectangle((75, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)

    # Left and right free throw circles
    l_free_throw = Circle((19, -25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)
    r_free_throw = Circle((75, -25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)

    # Left and right corner 3-PT lines
    # a represents the top lines
    # b represents the bottom lines
    l_corner_a = Rectangle((0, -3), 14, 0, lw=lw, color=color, zorder=zorder)
    l_corner_b = Rectangle((0, -47), 14, 0, lw=lw, color=color, zorder=zorder)
    r_corner_a = Rectangle((80, -3), 14, 0, lw=lw, color=color, zorder=zorder)
    r_corner_b = Rectangle((80, -47), 14, 0, lw=lw, color=color, zorder=zorder)

    # Left and right 3-PT line arcs
    l_arc = Arc((5, -25), 47.5, 47.5, theta1=292, theta2=68, lw=lw,
                color=color, zorder=zorder)
    r_arc = Arc((89, -25), 47.5, 47.5, theta1=112, theta2=248, lw=lw,
                color=color, zorder=zorder)

    # half_court
    # ax.axvline(470)
    half_court = Rectangle((47, -50), 0, 50, lw=lw, color=color, zorder=zorder)

    hc_big_circle = Circle((47, -25), radius=6, lw=lw, fill=False,
                           color=color, zorder=zorder)
    hc_sm_circle = Circle((47, -25), radius=2, lw=lw, fill=False,
                          color=color, zorder=zorder)

    court_elements = [l_hoop, l_backboard, l_outer_box, outer,
                      l_inner_box, l_free_throw, l_corner_a,
                      l_corner_b, l_arc, r_hoop, r_backboard,
                      r_outer_box, r_inner_box, r_free_throw,
                      r_corner_a, r_corner_b, r_arc, half_court,
                      hc_big_circle, hc_sm_circle]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax
