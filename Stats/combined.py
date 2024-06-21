import pandas as pd

from Stats.defense import defense_categories
from Stats.general import measure_types as general_measure_types
from Stats.playtype import play_types, defenses as play_type_defenses
from Stats.shooting import distance_ranges
from Stats.tracking import track_types

column_names_maps = {
    'Box Outs': {
        'old': ['PLAYER_ID', 'OFF_BOXOUTS', 'DEF_BOXOUTS', 'BOX_OUT_PLAYER_TEAM_REBS', 'BOX_OUT_PLAYER_REBS', 'BOX_OUTS', 'PCT_BOX_OUTS_OFF', 'PCT_BOX_OUTS_DEF', 'PCT_BOX_OUTS_TEAM_REB', 'PCT_BOX_OUTS_REB'],
        'new': ['PLAYER_ID', 'O_BOX_OUTS', 'D_BOX_OUTS', 'BOX_OUT_TEAM_REBS', 'BOX_OUT_REBS', 'BOX_OUTS', 'PCT_BOX_OUTS_O', 'PCT_BOX_OUTS_D', 'PCT_BOX_OUTS_TEAM_REB', 'PCT_BOX_OUTS_REB'],
    },
    'Defense': {
        '2 Pointers': {
            'old': ['CLOSE_DEF_PERSON_ID', 'FREQ', 'FG2M', 'FG2A', 'FG2_PCT', 'NS_FG2_PCT'],
            'new': ['PLAYER_ID', 'D_FG2_FREQ', 'D_FG2M', 'D_FG2A', 'D_FG2_PCT', 'D_NS_FG2_PCT'],
        },
        '3 Pointers': {
            'old': ['CLOSE_DEF_PERSON_ID', 'FREQ', 'FG3M', 'FG3A', 'FG3_PCT', 'NS_FG3_PCT'],
            'new': ['PLAYER_ID', 'D_FG3_FREQ', 'D_FG3M', 'D_FG3A', 'D_FG3_PCT', 'D_NS_FG3_PCT'],
        },
        'Greater Than 15Ft': {
            'old': ['CLOSE_DEF_PERSON_ID', 'FREQ', 'FGM_GT_15', 'FGA_GT_15', 'GT_15_PCT', 'NS_GT_15_PCT'],
            'new': ['PLAYER_ID', 'D_FG_GT_15_FREQ', 'D_FGM_GT_15', 'D_FGA_GT_15', 'D_GT_15_PCT', 'D_NS_GT_15_PCT'],
        },
        'Less Than 6Ft': {
            'old': ['CLOSE_DEF_PERSON_ID', 'FREQ', 'FGM_LT_06', 'FGA_LT_06', 'LT_06_PCT', 'NS_LT_06_PCT'],
            'new': ['PLAYER_ID', 'D_FG_LT_06_FREQ', 'D_FGM_LT_06', 'D_FGA_LT_06', 'D_LT_06_PCT', 'D_NS_LT_06_PCT'],
        },
        'Less Than 10Ft': {
            'old': ['CLOSE_DEF_PERSON_ID', 'FREQ', 'FGM_LT_10', 'FGA_LT_10', 'LT_10_PCT', 'NS_LT_10_PCT'],
            'new': ['PLAYER_ID', 'D_FG_LT_10_FREQ', 'D_FGM_LT_10', 'D_FGA_LT_10', 'D_LT_10_PCT', 'D_NS_LT_10_PCT'],
        },
        'Overall': {
            'old': ['CLOSE_DEF_PERSON_ID', 'D_FGM', 'D_FGA', 'D_FG_PCT', 'NORMAL_FG_PCT'],
            'new': ['PLAYER_ID', 'D_FGM', 'D_FGA', 'D_FG_PCT', 'D_NORMAL_FG_PCT'],
        },
    },
    'General': {
        'Advanced': {
            'old': ['PLAYER_ID', 'E_OFF_RATING', 'OFF_RATING', 'sp_work_OFF_RATING', 'E_DEF_RATING', 'DEF_RATING', 'sp_work_DEF_RATING', 'E_NET_RATING', 'NET_RATING', 'sp_work_NET_RATING', 'AST_PCT', 'AST_TO', 'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 'E_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'sp_work_PACE', 'PIE', 'POSS'],
            'new': ['PLAYER_ID', 'E_O_RATING', 'O_RATING', 'sp_work_O_RATING', 'E_D_RATING', 'D_RATING', 'sp_work_D_RATING', 'E_NET_RATING', 'NET_RATING', 'sp_work_NET_RATING', 'AST_PCT', 'AST_TO', 'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 'E_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'sp_work_PACE', 'PIE', 'POSS'],
        },
        'Base': {
            'old': ['PLAYER_ID', 'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'DD2', 'TD3'],
            'new': ['PLAYER_ID', 'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'DD2', 'TD3'],
        },
        'Defense': {
            'old': ['PLAYER_ID', 'DEF_WS'],
            'new': ['PLAYER_ID', 'DEF_WS'],
        },
        'Misc': {
            'old': ['PLAYER_ID', 'PTS_OFF_TOV', 'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT', 'OPP_PTS_OFF_TOV', 'OPP_PTS_2ND_CHANCE', 'OPP_PTS_FB', 'OPP_PTS_PAINT'],
            'new': ['PLAYER_ID', 'PTS_OFF_TOV', 'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT', 'OPP_PTS_OFF_TOV', 'OPP_PTS_2ND_CHANCE', 'OPP_PTS_FB', 'OPP_PTS_PAINT'],
        },
        'Scoring': {
            'old': ['PLAYER_ID', 'PCT_FGA_2PT', 'PCT_FGA_3PT', 'PCT_PTS_2PT', 'PCT_PTS_2PT_MR', 'PCT_PTS_3PT', 'PCT_PTS_FB', 'PCT_PTS_FT', 'PCT_PTS_OFF_TOV', 'PCT_PTS_PAINT', 'PCT_AST_2PM', 'PCT_UAST_2PM', 'PCT_AST_3PM', 'PCT_UAST_3PM', 'PCT_AST_FGM', 'PCT_UAST_FGM'],
            'new': ['PLAYER_ID', 'PCT_FGA_2PT', 'PCT_FGA_3PT', 'PCT_PTS_2PT', 'PCT_PTS_2PT_MR', 'PCT_PTS_3PT', 'PCT_PTS_FB', 'PCT_PTS_FT', 'PCT_PTS_OFF_TOV', 'PCT_PTS_PAINT', 'PCT_AST_2PM', 'PCT_UAST_2PM', 'PCT_AST_3PM', 'PCT_UAST_3PM', 'PCT_AST_FGM', 'PCT_UAST_FGM'],
        },
        'Usage': {
            'old': ['PLAYER_ID', 'PCT_FGM', 'PCT_FGA', 'PCT_FG3M', 'PCT_FG3A', 'PCT_FTM', 'PCT_FTA', 'PCT_OREB', 'PCT_DREB', 'PCT_REB', 'PCT_AST', 'PCT_TOV', 'PCT_STL', 'PCT_BLK', 'PCT_BLKA', 'PCT_PF', 'PCT_PFD', 'PCT_PTS'],
            'new': ['PLAYER_ID', 'PCT_TEAM_FGM', 'PCT_TEAM_FGA', 'PCT_TEAM_FG3M', 'PCT_TEAM_FG3A', 'PCT_TEAM_FTM', 'PCT_TEAM_FTA', 'PCT_TEAM_OREB', 'PCT_TEAM_DREB', 'PCT_TEAM_REB', 'PCT_TEAM_AST', 'PCT_TEAM_TOV', 'PCT_TEAM_STL', 'PCT_TEAM_BLK', 'PCT_TEAM_BLKA', 'PCT_TEAM_PF', 'PCT_TEAM_PFD', 'PCT_TEAM_PTS'],
        },
    },
    'Hustle': {
        'old': ['PLAYER_ID', 'CONTESTED_SHOTS', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'DEFLECTIONS', 'CHARGES_DRAWN', 'SCREEN_ASSISTS', 'SCREEN_AST_PTS', 'OFF_LOOSE_BALLS_RECOVERED', 'DEF_LOOSE_BALLS_RECOVERED', 'LOOSE_BALLS_RECOVERED', 'PCT_LOOSE_BALLS_RECOVERED_OFF', 'PCT_LOOSE_BALLS_RECOVERED_DEF'],
        'new': ['PLAYER_ID', 'CONTESTED_SHOTS', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'DEFLECTIONS', 'CHARGES_DRAWN', 'SCREEN_ASSISTS', 'SCREEN_AST_PTS', 'O_LOOSE_BALLS_RECOVERED', 'D_LOOSE_BALLS_RECOVERED', 'LOOSE_BALLS_RECOVERED', 'O_PCT_LOOSE_BALLS_RECOVERED', 'D_PCT_LOOSE_BALLS_RECOVERED'],
    },
    'Play Types': {
        'Cut': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_CUT_PERCENTILE', 'O_CUT_POSS_PCT', 'O_CUT_PPP', 'O_CUT_FG_PCT', 'O_CUT_FT_POSS_PCT', 'O_CUT_TOV_POSS_PCT', 'O_CUT_SF_POSS_PCT', 'O_CUT_PLUSONE_POSS_PCT', 'O_CUT_SCORE_POSS_PCT', 'O_CUT_EFG_PCT', 'O_CUT_POSS', 'O_CUT_PTS', 'O_CUT_FGM', 'O_CUT_FGA', 'O_CUT_FGMX'],
            },
            'defensive': {
                'old': [],
                'new': [],
            },
        },
        'Handoff': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_HANDOFF_PERCENTILE', 'O_HANDOFF_POSS_PCT', 'O_HANDOFF_PPP', 'O_HANDOFF_FG_PCT', 'O_HANDOFF_FT_POSS_PCT', 'O_HANDOFF_TOV_POSS_PCT', 'O_HANDOFF_SF_POSS_PCT', 'O_HANDOFF_PLUSONE_POSS_PCT', 'O_HANDOFF_SCORE_POSS_PCT', 'O_HANDOFF_EFG_PCT', 'O_HANDOFF_POSS', 'O_HANDOFF_PTS', 'O_HANDOFF_FGM', 'O_HANDOFF_FGA', 'O_HANDOFF_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_HANDOFF_PERCENTILE', 'D_HANDOFF_POSS_PCT', 'D_HANDOFF_PPP', 'D_HANDOFF_FG_PCT', 'D_HANDOFF_FT_POSS_PCT', 'D_HANDOFF_TOV_POSS_PCT', 'D_HANDOFF_SF_POSS_PCT', 'D_HANDOFF_PLUSONE_POSS_PCT', 'D_HANDOFF_SCORE_POSS_PCT', 'D_HANDOFF_EFG_PCT', 'D_HANDOFF_POSS', 'D_HANDOFF_PTS', 'D_HANDOFF_FGM', 'D_HANDOFF_FGA', 'D_HANDOFF_FGMX'],
            },
        },
        'Isolation': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_ISO_PERCENTILE', 'O_ISO_POSS_PCT', 'O_ISO_PPP', 'O_ISO_FG_PCT', 'O_ISO_FT_POSS_PCT', 'O_ISO_TOV_POSS_PCT', 'O_ISO_SF_POSS_PCT', 'O_ISO_PLUSONE_POSS_PCT', 'O_ISO_SCORE_POSS_PCT', 'O_ISO_EFG_PCT', 'O_ISO_POSS', 'O_ISO_PTS', 'O_ISO_FGM', 'O_ISO_FGA', 'O_ISO_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_ISO_PERCENTILE', 'D_ISO_POSS_PCT', 'D_ISO_PPP', 'D_ISO_FG_PCT', 'D_ISO_FT_POSS_PCT', 'D_ISO_TOV_POSS_PCT', 'D_ISO_SF_POSS_PCT', 'D_ISO_PLUSONE_POSS_PCT', 'D_ISO_SCORE_POSS_PCT', 'D_ISO_EFG_PCT', 'D_ISO_POSS', 'D_ISO_PTS', 'D_ISO_FGM', 'D_ISO_FGA', 'D_ISO_FGMX'],
            },
        },
        'Misc': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_MISC_PERCENTILE', 'O_MISC_POSS_PCT', 'O_MISC_PPP', 'O_MISC_FG_PCT', 'O_MISC_FT_POSS_PCT', 'O_MISC_TOV_POSS_PCT', 'O_MISC_SF_POSS_PCT', 'O_MISC_PLUSONE_POSS_PCT', 'O_MISC_SCORE_POSS_PCT', 'O_MISC_EFG_PCT', 'O_MISC_POSS', 'O_MISC_PTS', 'O_MISC_FGM', 'O_MISC_FGA', 'O_MISC_FGMX'],
            },
            'defensive': {
                'old': [],
                'new': [],
            },
        },
        'OffRebound': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_OFFREB_PERCENTILE', 'O_OFFREB_POSS_PCT', 'O_OFFREB_PPP', 'O_OFFREB_FG_PCT', 'O_OFFREB_FT_POSS_PCT', 'O_OFFREB_TOV_POSS_PCT', 'O_OFFREB_SF_POSS_PCT', 'O_OFFREB_PLUSONE_POSS_PCT', 'O_OFFREB_SCORE_POSS_PCT', 'O_OFFREB_EFG_PCT', 'O_OFFREB_POSS', 'O_OFFREB_PTS', 'O_OFFREB_FGM', 'O_OFFREB_FGA', 'O_OFFREB_FGMX'],
            },
            'defensive': {
                'old': [],
                'new': [],
            },
        },
        'OffScreen': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_OFFSCREEN_PERCENTILE', 'O_OFFSCREEN_POSS_PCT', 'O_OFFSCREEN_PPP', 'O_OFFSCREEN_FG_PCT', 'O_OFFSCREEN_FT_POSS_PCT', 'O_OFFSCREEN_TOV_POSS_PCT', 'O_OFFSCREEN_SF_POSS_PCT', 'O_OFFSCREEN_PLUSONE_POSS_PCT', 'O_OFFSCREEN_SCORE_POSS_PCT', 'O_OFFSCREEN_EFG_PCT', 'O_OFFSCREEN_POSS', 'O_OFFSCREEN_PTS', 'O_OFFSCREEN_FGM', 'O_OFFSCREEN_FGA', 'O_OFFSCREEN_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_OFFSCREEN_PERCENTILE', 'D_OFFSCREEN_POSS_PCT', 'D_OFFSCREEN_PPP', 'D_OFFSCREEN_FG_PCT', 'D_OFFSCREEN_FT_POSS_PCT', 'D_OFFSCREEN_TOV_POSS_PCT', 'D_OFFSCREEN_SF_POSS_PCT', 'D_OFFSCREEN_PLUSONE_POSS_PCT', 'D_OFFSCREEN_SCORE_POSS_PCT', 'D_OFFSCREEN_EFG_PCT', 'D_OFFSCREEN_POSS', 'D_OFFSCREEN_PTS', 'D_OFFSCREEN_FGM', 'D_OFFSCREEN_FGA', 'D_OFFSCREEN_FGMX'],
            },
        },
        'Postup': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_POSTUP_PERCENTILE', 'O_POSTUP_POSS_PCT', 'O_POSTUP_PPP', 'O_POSTUP_FG_PCT', 'O_POSTUP_FT_POSS_PCT', 'O_POSTUP_TOV_POSS_PCT', 'O_POSTUP_SF_POSS_PCT', 'O_POSTUP_PLUSONE_POSS_PCT', 'O_POSTUP_SCORE_POSS_PCT', 'O_POSTUP_EFG_PCT', 'O_POSTUP_POSS', 'O_POSTUP_PTS', 'O_POSTUP_FGM', 'O_POSTUP_FGA', 'O_POSTUP_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_POSTUP_PERCENTILE', 'D_POSTUP_POSS_PCT', 'D_POSTUP_PPP', 'D_POSTUP_FG_PCT', 'D_POSTUP_FT_POSS_PCT', 'D_POSTUP_TOV_POSS_PCT', 'D_POSTUP_SF_POSS_PCT', 'D_POSTUP_PLUSONE_POSS_PCT', 'D_POSTUP_SCORE_POSS_PCT', 'D_POSTUP_EFG_PCT', 'D_POSTUP_POSS', 'D_POSTUP_PTS', 'D_POSTUP_FGM', 'D_POSTUP_FGA', 'D_POSTUP_FGMX'],
            },
        },
        'PRBallHandler': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_PRBH_PERCENTILE', 'O_PRBH_POSS_PCT', 'O_PRBH_PPP', 'O_PRBH_FG_PCT', 'O_PRBH_FT_POSS_PCT', 'O_PRBH_TOV_POSS_PCT', 'O_PRBH_SF_POSS_PCT', 'O_PRBH_PLUSONE_POSS_PCT', 'O_PRBH_SCORE_POSS_PCT', 'O_PRBH_EFG_PCT', 'O_PRBH_POSS', 'O_PRBH_PTS', 'O_PRBH_FGM', 'O_PRBH_FGA', 'O_PRBH_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_PRBH_PERCENTILE', 'D_PRBH_POSS_PCT', 'D_PRBH_PPP', 'D_PRBH_FG_PCT', 'D_PRBH_FT_POSS_PCT', 'D_PRBH_TOV_POSS_PCT', 'D_PRBH_SF_POSS_PCT', 'D_PRBH_PLUSONE_POSS_PCT', 'D_PRBH_SCORE_POSS_PCT', 'D_PRBH_EFG_PCT', 'D_PRBH_POSS', 'D_PRBH_PTS', 'D_PRBH_FGM', 'D_PRBH_FGA', 'D_PRBH_FGMX'],
            },
        },
        'PRRollman': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_PRRM_PERCENTILE', 'O_PRRM_POSS_PCT', 'O_PRRM_PPP', 'O_PRRM_FG_PCT', 'O_PRRM_FT_POSS_PCT', 'O_PRRM_TOV_POSS_PCT', 'O_PRRM_SF_POSS_PCT', 'O_PRRM_PLUSONE_POSS_PCT', 'O_PRRM_SCORE_POSS_PCT', 'O_PRRM_EFG_PCT', 'O_PRRM_POSS', 'O_PRRM_PTS', 'O_PRRM_FGM', 'O_PRRM_FGA', 'O_PRRM_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_PRRM_PERCENTILE', 'D_PRRM_POSS_PCT', 'D_PRRM_PPP', 'D_PRRM_FG_PCT', 'D_PRRM_FT_POSS_PCT', 'D_PRRM_TOV_POSS_PCT', 'D_PRRM_SF_POSS_PCT', 'D_PRRM_PLUSONE_POSS_PCT', 'D_PRRM_SCORE_POSS_PCT', 'D_PRRM_EFG_PCT', 'D_PRRM_POSS', 'D_PRRM_PTS', 'D_PRRM_FGM', 'D_PRRM_FGA', 'D_PRRM_FGMX'],
            },
        },
        'Spotup': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_SPOTUP_PERCENTILE', 'O_SPOTUP_POSS_PCT', 'O_SPOTUP_PPP', 'O_SPOTUP_FG_PCT', 'O_SPOTUP_FT_POSS_PCT', 'O_SPOTUP_TOV_POSS_PCT', 'O_SPOTUP_SF_POSS_PCT', 'O_SPOTUP_PLUSONE_POSS_PCT', 'O_SPOTUP_SCORE_POSS_PCT', 'O_SPOTUP_EFG_PCT', 'O_SPOTUP_POSS', 'O_SPOTUP_PTS', 'O_SPOTUP_FGM', 'O_SPOTUP_FGA', 'O_SPOTUP_FGMX'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'D_SPOTUP_PERCENTILE', 'D_SPOTUP_POSS_PCT', 'D_SPOTUP_PPP', 'D_SPOTUP_FG_PCT', 'D_SPOTUP_FT_POSS_PCT', 'D_SPOTUP_TOV_POSS_PCT', 'D_SPOTUP_SF_POSS_PCT', 'D_SPOTUP_PLUSONE_POSS_PCT', 'D_SPOTUP_SCORE_POSS_PCT', 'D_SPOTUP_EFG_PCT', 'D_SPOTUP_POSS', 'D_SPOTUP_PTS', 'D_SPOTUP_FGM', 'D_SPOTUP_FGA', 'D_SPOTUP_FGMX'],
            },
        },
        'Transition': {
            'offensive': {
                'old': ['PLAYER_ID', 'PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX'],
                'new': ['PLAYER_ID', 'O_TRANS_PERCENTILE', 'O_TRANS_POSS_PCT', 'O_TRANS_PPP', 'O_TRANS_FG_PCT', 'O_TRANS_FT_POSS_PCT', 'O_TRANS_TOV_POSS_PCT', 'O_TRANS_SF_POSS_PCT', 'O_TRANS_PLUSONE_POSS_PCT', 'O_TRANS_SCORE_POSS_PCT', 'O_TRANS_EFG_PCT', 'O_TRANS_POSS', 'O_TRANS_PTS', 'O_TRANS_FGM', 'O_TRANS_FGA', 'O_TRANS_FGMX'],
            },
            'defensive': {
                'old': [],
                'new': [],
            },
        },
    },
    'Shooting': {
        '5ft Range': {
            'offensive': {
                'old': ['PLAYER_ID', 'Less Than 5 ft. FGM', 'Less Than 5 ft. FGA', 'Less Than 5 ft. FG_PCT', '5-9 ft. FGM', '5-9 ft. FGA', '5-9 ft. FG_PCT', '10-14 ft. FGM', '10-14 ft. FGA', '10-14 ft. FG_PCT', '15-19 ft. FGM', '15-19 ft. FGA', '15-19 ft. FG_PCT', '20-24 ft. FGM', '20-24 ft. FGA', '20-24 ft. FG_PCT', '25-29 ft. FGM', '25-29 ft. FGA', '25-29 ft. FG_PCT', '30-34 ft. FGM', '30-34 ft. FGA', '30-34 ft. FG_PCT', '35-39 ft. FGM', '35-39 ft. FGA', '35-39 ft. FG_PCT', '40+ ft. FGM', '40+ ft. FGA', '40+ ft. FG_PCT'],
                'new': ['PLAYER_ID', 'O_FGM_LT_05', 'O_FGA_LT_05', 'O_FG_PCT_LT_05', 'O_FGM_LT_10_GT_05', 'O_FGA_LT_10_GT_05', 'O_FG_PCT_LT_10_GT_05', 'O_FGM_LT_15_GT_10', 'O_FGA_LT_15_GT_10', 'O_FG_PCT_LT_15_GT_10', 'O_FGM_LT_20_GT_15', 'O_FGA_LT_20_GT_15', 'O_FG_PCT_LT_20_GT_15', 'O_FGM_LT_25_GT_20', 'O_FGA_LT_25_GT_20', 'O_FG_PCT_LT_25_GT_20', 'O_FGM_LT_30_GT_25', 'O_FGA_LT_30_GT_25', 'O_FG_PCT_LT_30_GT_25', 'O_FGM_LT_35_GT_30', 'O_FGA_LT_35_GT_30', 'O_FG_PCT_LT_35_GT_30', 'O_FGM_LT_40_GT_35', 'O_FGA_LT_40_GT_35', 'O_FG_PCT_LT_40_GT_35', 'O_FGM_GT_40', 'O_FGA_GT_40', 'O_FG_PCT_GT_40'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'Less Than 5 ft. OPP_FGM', 'Less Than 5 ft. OPP_FGA', 'Less Than 5 ft. OPP_FG_PCT', '5-9 ft. OPP_FGM', '5-9 ft. OPP_FGA', '5-9 ft. OPP_FG_PCT', '10-14 ft. OPP_FGM', '10-14 ft. OPP_FGA', '10-14 ft. OPP_FG_PCT', '15-19 ft. OPP_FGM', '15-19 ft. OPP_FGA', '15-19 ft. OPP_FG_PCT', '20-24 ft. OPP_FGM', '20-24 ft. OPP_FGA', '20-24 ft. OPP_FG_PCT', '25-29 ft. OPP_FGM', '25-29 ft. OPP_FGA', '25-29 ft. OPP_FG_PCT', '30-34 ft. OPP_FGM', '30-34 ft. OPP_FGA', '30-34 ft. OPP_FG_PCT', '35-39 ft. OPP_FGM', '35-39 ft. OPP_FGA', '35-39 ft. OPP_FG_PCT', '40+ ft. OPP_FGM', '40+ ft. OPP_FGA', '40+ ft. OPP_FG_PCT'],
                'new': ['PLAYER_ID', 'D_FGM_LT_05', 'D_FGA_LT_05', 'D_FG_PCT_LT_05', 'D_FGM_LT_10_GT_05', 'D_FGA_LT_10_GT_05', 'D_FG_PCT_LT_10_GT_05', 'D_FGM_LT_15_GT_10', 'D_FGA_LT_15_GT_10', 'D_FG_PCT_LT_15_GT_10', 'D_FGM_LT_20_GT_15', 'D_FGA_LT_20_GT_15', 'D_FG_PCT_LT_20_GT_15', 'D_FGM_LT_25_GT_20', 'D_FGA_LT_25_GT_20', 'D_FG_PCT_LT_25_GT_20', 'D_FGM_LT_30_GT_25', 'D_FGA_LT_30_GT_25', 'D_FG_PCT_LT_30_GT_25', 'D_FGM_LT_35_GT_30', 'D_FGA_LT_35_GT_30', 'D_FG_PCT_LT_35_GT_30', 'D_FGM_LT_40_GT_35', 'D_FGA_LT_40_GT_35', 'D_FG_PCT_LT_40_GT_35', 'D_FGM_GT_40', 'D_FGA_GT_40', 'D_FG_PCT_GT_40'],
            },
        },
        '8ft Range': {
            'offensive': {
                'old': ['PLAYER_ID', 'Less Than 8 ft. FGM', 'Less Than 8 ft. FGA', 'Less Than 8 ft. FG_PCT', '8-16 ft. FGM', '8-16 ft. FGA', '8-16 ft. FG_PCT', '16-24 ft. FGM', '16-24 ft. FGA', '16-24 ft. FG_PCT', '24+ ft. FGM', '24+ ft. FGA', '24+ ft. FG_PCT'],
                'new': ['PLAYER_ID', 'O_FGM_LT_08', 'O_FGA_LT_08', 'O_FG_PCT_LT_08', 'O_FGM_LT_16_GT_08', 'O_FGA_LT_16_GT_08', 'O_FG_PCT_LT_16_GT_08', 'O_FGM_LT_24_GT_16', 'O_FGA_LT_24_GT_16', 'O_FG_PCT_LT_24_GT_16', 'O_FGM_GT_24', 'O_FGA_GT_24', 'O_FG_PCT_GT_24'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'Less Than 8 ft. OPP_FGM', 'Less Than 8 ft. OPP_FGA', 'Less Than 8 ft. OPP_FG_PCT', '8-16 ft. OPP_FGM', '8-16 ft. OPP_FGA', '8-16 ft. OPP_FG_PCT', '16-24 ft. OPP_FGM', '16-24 ft. OPP_FGA', '16-24 ft. OPP_FG_PCT', '24+ ft. OPP_FGM', '24+ ft. OPP_FGA', '24+ ft. OPP_FG_PCT'],
                'new': ['PLAYER_ID', 'D_FGM_LT_08', 'D_FGA_LT_08', 'D_FG_PCT_LT_08', 'D_FGM_LT_16_GT_08', 'D_FGA_LT_16_GT_08', 'D_FG_PCT_LT_16_GT_08', 'D_FGM_LT_24_GT_16', 'D_FGA_LT_24_GT_16', 'D_FG_PCT_LT_24_GT_16', 'D_FGM_GT_24', 'D_FGA_GT_24', 'D_FG_PCT_GT_24'],
            },
        },
        'By Zone': {
            'offensive': {
                'old': ['PLAYER_ID', 'Restricted Area FGM', 'Restricted Area FGA', 'Restricted Area FG_PCT', 'In The Paint (Non-RA) FGM', 'In The Paint (Non-RA) FGA', 'In The Paint (Non-RA) FG_PCT', 'Mid-Range FGM', 'Mid-Range FGA', 'Mid-Range FG_PCT', 'Left Corner 3 FGM', 'Left Corner 3 FGA', 'Left Corner 3 FG_PCT', 'Right Corner 3 FGM', 'Right Corner 3 FGA', 'Right Corner 3 FG_PCT', 'Above the Break 3 FGM', 'Above the Break 3 FGA', 'Above the Break 3 FG_PCT', 'Backcourt FGM', 'Backcourt FGA', 'Backcourt FG_PCT', 'Corner 3 FGM', 'Corner 3 FGA', 'Corner 3 FG_PCT'],
                'new': ['PLAYER_ID', 'O_FGM_RA', 'O_FGA_RA', 'O_FG_PCT_RA', 'O_FGM_PAINT_NRA', 'O_FGA_PAINT_NRA', 'O_FG_PCT_PAINT_NRA', 'O_FGM_MR', 'O_FGA_MR', 'O_FG_PCT_MR', 'O_FGM_LC3', 'O_FGA_LC3', 'O_FG_PCT_LC3', 'O_FGM_RC3', 'O_FGA_RC3', 'O_FG_PCT_RC3', 'O_FGM_AB3', 'O_FGA_AB3', 'O_FG_PCT_AB3', 'O_FGM_BC', 'O_FGA_BC', 'O_FG_PCT_BC', 'O_FGM_C3', 'O_FGA_C3', 'O_FG_PCT_C3'],
            },
            'defensive': {
                'old': ['PLAYER_ID', 'Restricted Area OPP_FGM', 'Restricted Area OPP_FGA', 'Restricted Area OPP_FG_PCT', 'In The Paint (Non-RA) OPP_FGM', 'In The Paint (Non-RA) OPP_FGA', 'In The Paint (Non-RA) OPP_FG_PCT', 'Mid-Range OPP_FGM', 'Mid-Range OPP_FGA', 'Mid-Range OPP_FG_PCT', 'Left Corner 3 OPP_FGM', 'Left Corner 3 OPP_FGA', 'Left Corner 3 OPP_FG_PCT', 'Right Corner 3 OPP_FGM', 'Right Corner 3 OPP_FGA', 'Right Corner 3 OPP_FG_PCT', 'Above the Break 3 OPP_FGM', 'Above the Break 3 OPP_FGA', 'Above the Break 3 OPP_FG_PCT', 'Backcourt OPP_FGM', 'Backcourt OPP_FGA', 'Backcourt OPP_FG_PCT', 'Corner 3 OPP_FGM', 'Corner 3 OPP_FGA', 'Corner 3 OPP_FG_PCT'],
                'new': ['PLAYER_ID', 'D_FGM_RA', 'D_FGA_RA', 'D_FG_PCT_RA', 'D_FGM_PAINT_NRA', 'D_FGA_PAINT_NRA', 'D_FG_PCT_PAINT_NRA', 'D_FGM_MR', 'D_FGA_MR', 'D_FG_PCT_MR', 'D_FGM_LC3', 'D_FGA_LC3', 'D_FG_PCT_LC3', 'D_FGM_RC3', 'D_FGA_RC3', 'D_FG_PCT_RC3', 'D_FGM_AB3', 'D_FGA_AB3', 'D_FG_PCT_AB3', 'D_FGM_BC', 'D_FGA_BC', 'D_FG_PCT_BC', 'D_FGM_C3', 'D_FGA_C3', 'D_FG_PCT_C3'],
            },
        },
    },
    'Tracking': {
        'CatchShoot': {
            'old': ['PLAYER_ID', 'CATCH_SHOOT_FGM', 'CATCH_SHOOT_FGA', 'CATCH_SHOOT_FG_PCT', 'CATCH_SHOOT_PTS', 'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A', 'CATCH_SHOOT_FG3_PCT', 'CATCH_SHOOT_EFG_PCT'],
            'new': ['PLAYER_ID', 'CATCH_SHOOT_FGM', 'CATCH_SHOOT_FGA', 'CATCH_SHOOT_FG_PCT', 'CATCH_SHOOT_PTS', 'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A', 'CATCH_SHOOT_FG3_PCT', 'CATCH_SHOOT_EFG_PCT'],
        },
        'Defense': {
            'old': ['PLAYER_ID', 'DEF_RIM_FGM', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT'],
            'new': ['PLAYER_ID', 'D_RIM_FGM', 'D_RIM_FGA', 'D_RIM_FG_PCT'],
        },
        'Drives': {
            'old': ['PLAYER_ID', 'DRIVES', 'DRIVE_FGM', 'DRIVE_FGA', 'DRIVE_FG_PCT', 'DRIVE_FTM', 'DRIVE_FTA', 'DRIVE_FT_PCT', 'DRIVE_PTS', 'DRIVE_PTS_PCT', 'DRIVE_PASSES', 'DRIVE_PASSES_PCT', 'DRIVE_AST', 'DRIVE_AST_PCT', 'DRIVE_TOV', 'DRIVE_TOV_PCT', 'DRIVE_PF', 'DRIVE_PF_PCT'],
            'new': ['PLAYER_ID', 'DRIVES', 'DRIVE_FGM', 'DRIVE_FGA', 'DRIVE_FG_PCT', 'DRIVE_FTM', 'DRIVE_FTA', 'DRIVE_FT_PCT', 'DRIVE_PTS', 'DRIVE_PTS_PCT', 'DRIVE_PASSES', 'DRIVE_PASSES_PCT', 'DRIVE_AST', 'DRIVE_AST_PCT', 'DRIVE_TOV', 'DRIVE_TOV_PCT', 'DRIVE_PF', 'DRIVE_PF_PCT'],
        },
        'Efficiency': {
            'old': ['PLAYER_ID'],
            'new': ['PLAYER_ID'],
        },
        'ElbowTouch': {
            'old': ['PLAYER_ID', 'ELBOW_TOUCHES', 'ELBOW_TOUCH_FGM', 'ELBOW_TOUCH_FGA', 'ELBOW_TOUCH_FG_PCT', 'ELBOW_TOUCH_FTM', 'ELBOW_TOUCH_FTA', 'ELBOW_TOUCH_FT_PCT', 'ELBOW_TOUCH_PTS', 'ELBOW_TOUCH_PASSES', 'ELBOW_TOUCH_AST', 'ELBOW_TOUCH_AST_PCT', 'ELBOW_TOUCH_TOV', 'ELBOW_TOUCH_TOV_PCT', 'ELBOW_TOUCH_FOULS', 'ELBOW_TOUCH_PASSES_PCT', 'ELBOW_TOUCH_FOULS_PCT', 'ELBOW_TOUCH_PTS_PCT'],
            'new': ['PLAYER_ID', 'ELBOW_TOUCHES', 'ELBOW_TOUCH_FGM', 'ELBOW_TOUCH_FGA', 'ELBOW_TOUCH_FG_PCT', 'ELBOW_TOUCH_FTM', 'ELBOW_TOUCH_FTA', 'ELBOW_TOUCH_FT_PCT', 'ELBOW_TOUCH_PTS', 'ELBOW_TOUCH_PASSES', 'ELBOW_TOUCH_AST', 'ELBOW_TOUCH_AST_PCT', 'ELBOW_TOUCH_TOV', 'ELBOW_TOUCH_TOV_PCT', 'ELBOW_TOUCH_FOULS', 'ELBOW_TOUCH_PASSES_PCT', 'ELBOW_TOUCH_FOULS_PCT', 'ELBOW_TOUCH_PTS_PCT'],
        },
        'PaintTouch': {
            'old': ['PLAYER_ID', 'PAINT_TOUCHES', 'PAINT_TOUCH_FGM', 'PAINT_TOUCH_FGA', 'PAINT_TOUCH_FG_PCT', 'PAINT_TOUCH_FTM', 'PAINT_TOUCH_FTA', 'PAINT_TOUCH_FT_PCT', 'PAINT_TOUCH_PTS', 'PAINT_TOUCH_PTS_PCT', 'PAINT_TOUCH_PASSES', 'PAINT_TOUCH_PASSES_PCT', 'PAINT_TOUCH_AST', 'PAINT_TOUCH_AST_PCT', 'PAINT_TOUCH_TOV', 'PAINT_TOUCH_TOV_PCT', 'PAINT_TOUCH_FOULS', 'PAINT_TOUCH_FOULS_PCT'],
            'new': ['PLAYER_ID', 'PAINT_TOUCHES', 'PAINT_TOUCH_FGM', 'PAINT_TOUCH_FGA', 'PAINT_TOUCH_FG_PCT', 'PAINT_TOUCH_FTM', 'PAINT_TOUCH_FTA', 'PAINT_TOUCH_FT_PCT', 'PAINT_TOUCH_PTS', 'PAINT_TOUCH_PTS_PCT', 'PAINT_TOUCH_PASSES', 'PAINT_TOUCH_PASSES_PCT', 'PAINT_TOUCH_AST', 'PAINT_TOUCH_AST_PCT', 'PAINT_TOUCH_TOV', 'PAINT_TOUCH_TOV_PCT', 'PAINT_TOUCH_FOULS', 'PAINT_TOUCH_FOULS_PCT'],
        },
        'Passing': {
            'old': ['PLAYER_ID', 'PASSES_MADE', 'PASSES_RECEIVED', 'FT_AST', 'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED', 'AST_ADJ', 'AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ'],
            'new': ['PLAYER_ID', 'PASSES_MADE', 'PASSES_RECEIVED', 'FT_AST', 'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED', 'AST_ADJ', 'AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ'],
        },
        'Possessions': {
            'old': ['PLAYER_ID', 'TOUCHES', 'FRONT_CT_TOUCHES', 'TIME_OF_POSS', 'AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH', 'PTS_PER_TOUCH'],
            'new': ['PLAYER_ID', 'TOUCHES', 'FRONT_CT_TOUCHES', 'TIME_OF_POSS', 'AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH', 'PTS_PER_TOUCH'],
        },
        'PostTouch': {
            'old': ['PLAYER_ID', 'POST_TOUCHES', 'POST_TOUCH_FGM', 'POST_TOUCH_FGA', 'POST_TOUCH_FG_PCT', 'POST_TOUCH_FTM', 'POST_TOUCH_FTA', 'POST_TOUCH_FT_PCT', 'POST_TOUCH_PTS', 'POST_TOUCH_PTS_PCT', 'POST_TOUCH_PASSES', 'POST_TOUCH_PASSES_PCT', 'POST_TOUCH_AST', 'POST_TOUCH_AST_PCT', 'POST_TOUCH_TOV', 'POST_TOUCH_TOV_PCT', 'POST_TOUCH_FOULS', 'POST_TOUCH_FOULS_PCT'],
            'new': ['PLAYER_ID', 'POST_TOUCHES', 'POST_TOUCH_FGM', 'POST_TOUCH_FGA', 'POST_TOUCH_FG_PCT', 'POST_TOUCH_FTM', 'POST_TOUCH_FTA', 'POST_TOUCH_FT_PCT', 'POST_TOUCH_PTS', 'POST_TOUCH_PTS_PCT', 'POST_TOUCH_PASSES', 'POST_TOUCH_PASSES_PCT', 'POST_TOUCH_AST', 'POST_TOUCH_AST_PCT', 'POST_TOUCH_TOV', 'POST_TOUCH_TOV_PCT', 'POST_TOUCH_FOULS', 'POST_TOUCH_FOULS_PCT'],
        },
        'PullUpShot': {
            'old': ['PLAYER_ID', 'PULL_UP_FGM', 'PULL_UP_FGA', 'PULL_UP_FG_PCT', 'PULL_UP_PTS', 'PULL_UP_FG3M', 'PULL_UP_FG3A', 'PULL_UP_FG3_PCT', 'PULL_UP_EFG_PCT'],
            'new': ['PLAYER_ID', 'PULL_UP_FGM', 'PULL_UP_FGA', 'PULL_UP_FG_PCT', 'PULL_UP_PTS', 'PULL_UP_FG3M', 'PULL_UP_FG3A', 'PULL_UP_FG3_PCT', 'PULL_UP_EFG_PCT'],
        },
        'Rebounding': {
            'old': ['PLAYER_ID', 'OREB_CONTEST', 'OREB_UNCONTEST', 'OREB_CONTEST_PCT', 'OREB_CHANCES', 'OREB_CHANCE_PCT', 'OREB_CHANCE_DEFER', 'OREB_CHANCE_PCT_ADJ', 'AVG_OREB_DIST', 'DREB_CONTEST', 'DREB_UNCONTEST', 'DREB_CONTEST_PCT', 'DREB_CHANCES', 'DREB_CHANCE_PCT', 'DREB_CHANCE_DEFER', 'DREB_CHANCE_PCT_ADJ', 'AVG_DREB_DIST', 'REB_CONTEST', 'REB_UNCONTEST', 'REB_CONTEST_PCT', 'REB_CHANCES', 'REB_CHANCE_PCT', 'REB_CHANCE_DEFER', 'REB_CHANCE_PCT_ADJ', 'AVG_REB_DIST'],
            'new': ['PLAYER_ID', 'OREB_CONTEST', 'OREB_UNCONTEST', 'OREB_CONTEST_PCT', 'OREB_CHANCES', 'OREB_CHANCE_PCT', 'OREB_CHANCE_DEFER', 'OREB_CHANCE_PCT_ADJ', 'AVG_OREB_DIST', 'DREB_CONTEST', 'DREB_UNCONTEST', 'DREB_CONTEST_PCT', 'DREB_CHANCES', 'DREB_CHANCE_PCT', 'DREB_CHANCE_DEFER', 'DREB_CHANCE_PCT_ADJ', 'AVG_DREB_DIST', 'REB_CONTEST', 'REB_UNCONTEST', 'REB_CONTEST_PCT', 'REB_CHANCES', 'REB_CHANCE_PCT', 'REB_CHANCE_DEFER', 'REB_CHANCE_PCT_ADJ', 'AVG_REB_DIST'],
        },
        'SpeedDistance': {
            'old': ['PLAYER_ID', 'DIST_FEET', 'DIST_MILES', 'DIST_MILES_OFF', 'DIST_MILES_DEF', 'AVG_SPEED', 'AVG_SPEED_OFF', 'AVG_SPEED_DEF'],
            'new': ['PLAYER_ID', 'DIST_FEET', 'DIST_MILES', 'DIST_MILES_O', 'DIST_MILES_D', 'AVG_SPEED', 'AVG_SPEED_O', 'AVG_SPEED_D'],
        },
    },
}

rate_adjusted_columns = {
    'Box Outs': ['O_BOX_OUTS', 'D_BOX_OUTS', 'BOX_OUT_TEAM_REBS', 'BOX_OUT_REBS', 'BOX_OUTS'],
    'Defense': {
        '2 Pointers': ['D_FG2M', 'D_FG2A'],
        '3 Pointers': ['D_FG3M', 'D_FG3A'],
        'Greater Than 15Ft': ['D_FGM_GT_15', 'D_FGA_GT_15'],
        'Less Than 6Ft': ['D_FGM_LT_06', 'D_FGA_LT_06'],
        'Less Than 10Ft': ['D_FGM_LT_10', 'D_FGA_LT_10'],
        'Overall': ['D_FGM', 'D_FGA'],
    },
    'General': {
        'Advanced': [],
        'Base': ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK',
                 'BLKA', 'PF', 'PFD', 'PTS'],
        'Defense': [],
        'Misc': ['PTS_OFF_TOV', 'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT', 'OPP_PTS_OFF_TOV', 'OPP_PTS_2ND_CHANCE',
                 'OPP_PTS_FB', 'OPP_PTS_PAINT'],
        'Scoring': [],
        'Usage': [],
    },
    'Hustle': ['CONTESTED_SHOTS', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'DEFLECTIONS', 'CHARGES_DRAWN',
               'SCREEN_ASSISTS', 'SCREEN_AST_PTS', 'O_LOOSE_BALLS_RECOVERED', 'D_LOOSE_BALLS_RECOVERED',
               'LOOSE_BALLS_RECOVERED'],
    'Play Types': {
        'Cut': {
            'offensive': ['O_CUT_POSS', 'O_CUT_PTS', 'O_CUT_FGM', 'O_CUT_FGA', 'O_CUT_FGMX'],
            'defensive': [],
        },
        'Handoff': {
            'offensive': ['O_HANDOFF_POSS', 'O_HANDOFF_PTS', 'O_HANDOFF_FGM', 'O_HANDOFF_FGA', 'O_HANDOFF_FGMX'],
            'defensive': ['D_HANDOFF_POSS', 'D_HANDOFF_PTS', 'D_HANDOFF_FGM', 'D_HANDOFF_FGA', 'D_HANDOFF_FGMX'],
        },
        'Isolation': {
            'offensive': ['O_ISO_POSS', 'O_ISO_PTS', 'O_ISO_FGM', 'O_ISO_FGA', 'O_ISO_FGMX'],
            'defensive': ['D_ISO_POSS', 'D_ISO_PTS', 'D_ISO_FGM', 'D_ISO_FGA', 'D_ISO_FGMX'],
        },
        'Misc': {
            'offensive': ['O_MISC_POSS', 'O_MISC_PTS', 'O_MISC_FGM', 'O_MISC_FGA', 'O_MISC_FGMX'],
            'defensive': [],
        },
        'OffRebound': {
            'offensive': ['O_OFFREB_POSS', 'O_OFFREB_PTS', 'O_OFFREB_FGM', 'O_OFFREB_FGA', 'O_OFFREB_FGMX'],
            'defensive': [],
        },
        'OffScreen': {
            'offensive': ['O_OFFSCREEN_POSS', 'O_OFFSCREEN_PTS', 'O_OFFSCREEN_FGM', 'O_OFFSCREEN_FGA',
                          'O_OFFSCREEN_FGMX'],
            'defensive': ['D_OFFSCREEN_POSS', 'D_OFFSCREEN_PTS', 'D_OFFSCREEN_FGM', 'D_OFFSCREEN_FGA',
                          'D_OFFSCREEN_FGMX'],
        },
        'Postup': {
            'offensive': ['O_POSTUP_POSS', 'O_POSTUP_PTS', 'O_POSTUP_FGM', 'O_POSTUP_FGA', 'O_POSTUP_FGMX'],
            'defensive': ['D_POSTUP_POSS', 'D_POSTUP_PTS', 'D_POSTUP_FGM', 'D_POSTUP_FGA', 'D_POSTUP_FGMX'],
        },
        'PRBallHandler': {
            'offensive': ['O_PRBH_POSS', 'O_PRBH_PTS', 'O_PRBH_FGM', 'O_PRBH_FGA', 'O_PRBH_FGMX'],
            'defensive': ['D_PRBH_POSS', 'D_PRBH_PTS', 'D_PRBH_FGM', 'D_PRBH_FGA', 'D_PRBH_FGMX'],
        },
        'PRRollman': {
            'offensive': ['O_PRRM_POSS', 'O_PRRM_PTS', 'O_PRRM_FGM', 'O_PRRM_FGA', 'O_PRRM_FGMX'],
            'defensive': ['D_PRRM_POSS', 'D_PRRM_PTS', 'D_PRRM_FGM', 'D_PRRM_FGA', 'D_PRRM_FGMX'],
        },
        'Spotup': {
            'offensive': ['O_SPOTUP_POSS', 'O_SPOTUP_PTS', 'O_SPOTUP_FGM', 'O_SPOTUP_FGA', 'O_SPOTUP_FGMX'],
            'defensive': ['D_SPOTUP_POSS', 'D_SPOTUP_PTS', 'D_SPOTUP_FGM', 'D_SPOTUP_FGA', 'D_SPOTUP_FGMX'],
        },
        'Transition': {
            'offensive': ['O_TRANS_POSS', 'O_TRANS_PTS', 'O_TRANS_FGM', 'O_TRANS_FGA', 'O_TRANS_FGMX'],
            'defensive': [],
        },
    },
    'Shooting': {
        '5ft Range': {
            'offensive': ['O_FGM_LT_05', 'O_FGA_LT_05', 'O_FGM_LT_10_GT_05', 'O_FGA_LT_10_GT_05', 'O_FGM_LT_15_GT_10',
                          'O_FGA_LT_15_GT_10', 'O_FGM_LT_20_GT_15', 'O_FGA_LT_20_GT_15', 'O_FGM_LT_25_GT_20',
                          'O_FGA_LT_25_GT_20', 'O_FGM_LT_30_GT_25', 'O_FGA_LT_30_GT_25', 'O_FGM_LT_35_GT_30',
                          'O_FGA_LT_35_GT_30', 'O_FGM_LT_40_GT_35', 'O_FGA_LT_40_GT_35', 'O_FGM_GT_40', 'O_FGA_GT_40'],
            'defensive': ['D_FGM_LT_05', 'D_FGA_LT_05', 'D_FGM_LT_10_GT_05', 'D_FGA_LT_10_GT_05', 'D_FGM_LT_15_GT_10',
                          'D_FGA_LT_15_GT_10', 'D_FGM_LT_20_GT_15', 'D_FGA_LT_20_GT_15', 'D_FGM_LT_25_GT_20',
                          'D_FGA_LT_25_GT_20', 'D_FGM_LT_30_GT_25', 'D_FGA_LT_30_GT_25', 'D_FGM_LT_35_GT_30',
                          'D_FGA_LT_35_GT_30', 'D_FGM_LT_40_GT_35', 'D_FGA_LT_40_GT_35', 'D_FGM_GT_40', 'D_FGA_GT_40'],
        },
        '8ft Range': {
            'offensive': ['O_FGM_LT_08', 'O_FGA_LT_08', 'O_FGM_LT_16_GT_08', 'O_FGA_LT_16_GT_08', 'O_FGM_LT_24_GT_16',
                          'O_FGA_LT_24_GT_16', 'O_FGM_GT_24', 'O_FGA_GT_24'],
            'defensive': ['D_FGM_LT_08', 'D_FGA_LT_08', 'D_FGM_LT_16_GT_08', 'D_FGA_LT_16_GT_08', 'D_FGM_LT_24_GT_16',
                          'D_FGA_LT_24_GT_16', 'D_FGM_GT_24', 'D_FGA_GT_24'],
        },
        'By Zone': {
            'offensive': ['O_FGM_RA', 'O_FGA_RA', 'O_FGM_PAINT_NRA', 'O_FGA_PAINT_NRA', 'O_FGM_MR', 'O_FGA_MR',
                          'O_FGM_LC3', 'O_FGA_LC3', 'O_FGM_RC3', 'O_FGA_RC3', 'O_FGM_AB3', 'O_FGA_AB3', 'O_FGM_BC',
                          'O_FGA_BC', 'O_FGM_C3', 'O_FGA_C3'],
            'defensive': ['D_FGM_RA', 'D_FGA_RA', 'D_FGM_PAINT_NRA', 'D_FGA_PAINT_NRA', 'D_FGM_MR', 'D_FGA_MR',
                          'D_FGM_LC3', 'D_FGA_LC3', 'D_FGM_RC3', 'D_FGA_RC3', 'D_FGM_AB3', 'D_FGA_AB3', 'D_FGM_BC',
                          'D_FGA_BC', 'D_FGM_C3', 'D_FGA_C3'],
        },
    },
    'Tracking': {
        'CatchShoot': ['CATCH_SHOOT_FGM', 'CATCH_SHOOT_FGA', 'CATCH_SHOOT_PTS', 'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A'],
        'Defense': ['D_RIM_FGM', 'D_RIM_FGA'],
        'Drives': ['DRIVES', 'DRIVE_FGM', 'DRIVE_FGA', 'DRIVE_FTM', 'DRIVE_FTA', 'DRIVE_PTS', 'DRIVE_PASSES',
                   'DRIVE_AST', 'DRIVE_TOV', 'DRIVE_PF'],
        'Efficiency': [],
        'ElbowTouch': ['ELBOW_TOUCHES', 'ELBOW_TOUCH_FGM', 'ELBOW_TOUCH_FGA', 'ELBOW_TOUCH_FTM', 'ELBOW_TOUCH_FTA',
                       'ELBOW_TOUCH_PTS', 'ELBOW_TOUCH_PASSES', 'ELBOW_TOUCH_AST', 'ELBOW_TOUCH_TOV',
                       'ELBOW_TOUCH_FOULS'],
        'PaintTouch': ['PAINT_TOUCHES', 'PAINT_TOUCH_FGM', 'PAINT_TOUCH_FGA', 'PAINT_TOUCH_FTM', 'PAINT_TOUCH_FTA',
                       'PAINT_TOUCH_PTS', 'PAINT_TOUCH_PASSES', 'PAINT_TOUCH_AST', 'PAINT_TOUCH_TOV',
                       'PAINT_TOUCH_FOULS'],
        'Passing': ['PASSES_MADE', 'PASSES_RECEIVED', 'FT_AST', 'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED',
                    'AST_ADJ'],
        'Possessions': ['TOUCHES', 'FRONT_CT_TOUCHES'],
        'PostTouch': ['POST_TOUCHES', 'POST_TOUCH_FGM', 'POST_TOUCH_FGA', 'POST_TOUCH_FTM', 'POST_TOUCH_FTA',
                      'POST_TOUCH_PTS', 'POST_TOUCH_PASSES', 'POST_TOUCH_AST', 'POST_TOUCH_TOV', 'POST_TOUCH_FOULS'],
        'PullUpShot': ['PULL_UP_FGM', 'PULL_UP_FGA', 'PULL_UP_PTS', 'PULL_UP_FG3M', 'PULL_UP_FG3A'],
        'Rebounding': ['OREB_CONTEST', 'OREB_UNCONTEST', 'OREB_CHANCES', 'OREB_CHANCE_DEFER',
                       'DREB_CONTEST', 'DREB_UNCONTEST', 'DREB_CHANCES', 'DREB_CHANCE_DEFER',
                       'REB_CONTEST', 'REB_UNCONTEST', 'REB_CHANCES', 'REB_CHANCE_DEFER'],
        'SpeedDistance': ['DIST_FEET', 'DIST_MILES', 'DIST_MILES_O', 'DIST_MILES_D'],
    },
}


# Get the availability of stats based on the season
def get_availability(season):
    if season >= '2017-18':
        availability = {
            'Box Outs': True,
            'Defense': True,
            'General': True,
            'Hustle': True,
            'Play Types': True,
            'Shooting': True,
            'Tracking': True
        }
    elif season >= '2015-16':
        availability = {
            'Box Outs': False,
            'Defense': True,
            'General': True,
            'Hustle': True,
            'Play Types': True,
            'Shooting': True,
            'Tracking': True
        }
    elif season >= '2013-14':
        availability = {
            'Box Outs': False,
            'Defense': True,
            'General': True,
            'Hustle': False,
            'Play Types': False,
            'Shooting': True,
            'Tracking': True
        }
    else:
        availability = {
            'Box Outs': False,
            'Defense': False,
            'General': True,
            'Hustle': False,
            'Play Types': False,
            'Shooting': True,
            'Tracking': False
        }
    return availability


# Get data from a csv file, filter it, and update the column names
def get_data_and_change_columns(data_filename, column_names_map):
    stats = pd.read_csv(data_filename)
    filtered_stats = stats[column_names_map['old']]
    filtered_stats.columns = column_names_map['new']
    return filtered_stats
    
    
# Combine different stat categories for a single season
def combine_single_season_stats(season, season_type, save_filename):
    # Get availability of stats
    availability = get_availability(season)

    # Get each available stat type
    stat_types = list(availability.keys())

    # Merge all stats together for this season
    combined = pd.DataFrame(columns=['PLAYER_ID'])
    for stat_type in stat_types:
        if availability[stat_type]:
            # Get box outs and hustle stats
            if stat_type == 'Box Outs' or stat_type == 'Hustle':
                column_names_map = column_names_maps[stat_type]
                stats = get_data_and_change_columns(f'../Data/SeasonStats/Hustle/{season}_{season_type}.csv', column_names_map)

                # Merge with other stats
                combined = combined.merge(stats, on='PLAYER_ID', how='outer')

            # Get defensive stats
            elif stat_type == 'Defense':
                for defense_category in defense_categories:
                    column_names_map = column_names_maps[stat_type][defense_category]
                    stats = get_data_and_change_columns(f'../Data/SeasonStats/Defense/{defense_category}/{season}_{season_type}.csv', column_names_map)

                    # Merge with other stats
                    combined = combined.merge(stats, on='PLAYER_ID', how='outer')

            # Get general stats
            elif stat_type == 'General':
                for general_measure_type in general_measure_types:
                    column_names_map = column_names_maps[stat_type][general_measure_type]
                    stats = get_data_and_change_columns(f'../Data/SeasonStats/General/{general_measure_type}/{season}_{season_type}.csv',column_names_map)

                    # Merge with other stats
                    combined = combined.merge(stats, on='PLAYER_ID', how='outer')

            # Get play type stats
            elif stat_type == 'Play Types':
                for play_type, defense in zip(play_types, play_type_defenses):
                    o_column_names_map = column_names_maps[stat_type][play_type]['offensive']
                    o_stats = get_data_and_change_columns(f'../Data/SeasonStats/PlayTypes/{play_type}/{season}_{season_type}_offensive.csv', o_column_names_map)

                    # Merge with other stats
                    combined = combined.merge(o_stats, on='PLAYER_ID', how='outer')

                    if defense:
                        d_column_names_map = column_names_maps[stat_type][play_type]['defensive']
                        d_stats = get_data_and_change_columns(f'../Data/SeasonStats/PlayTypes/{play_type}/{season}_{season_type}_defensive.csv', d_column_names_map)

                        # Merge with other stats
                        combined = combined.merge(d_stats, on='PLAYER_ID', how='outer')

            # Get shooting stats
            elif stat_type == 'Shooting':
                for distance_range in distance_ranges:
                    o_column_names_map = column_names_maps[stat_type][distance_range]['offensive']
                    o_stats = get_data_and_change_columns(f'../Data/SeasonStats/Shooting/{distance_range}/{season}_{season_type}_Base.csv', o_column_names_map)

                    # Merge with other stats
                    combined = combined.merge(o_stats, on='PLAYER_ID', how='outer')

                    d_column_names_map = column_names_maps[stat_type][distance_range]['defensive']
                    d_stats = get_data_and_change_columns(f'../Data/SeasonStats/Shooting/{distance_range}/{season}_{season_type}_Opponent.csv', d_column_names_map)

                    # Merge with other stats
                    combined = combined.merge(d_stats, on='PLAYER_ID', how='outer')

            # Get tracking stats
            elif stat_type == 'Tracking':
                for track_type in track_types:
                    column_names_map = column_names_maps[stat_type][track_type]
                    stats = get_data_and_change_columns(f'../Data/SeasonStats/Tracking/{track_type}/{season}_{season_type}.csv', column_names_map)

                    # Merge with other stats
                    combined = combined.merge(stats, on='PLAYER_ID', how='outer')

    # Save combined stats to csv
    combined.to_csv(save_filename.format(season, season_type), index=False)


# Combine stats one season at a time for every season
def combine_stats_seasons(seasons, season_types, save_filename):
    # Combine stats for each season
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            percent_done = ((i * n_season_types + j) /(n_seasons * n_season_types))
            print(f'{percent_done:.2%} {season} {season_type}')

            # Combine stats for this season
            combine_single_season_stats(season, season_type, save_filename)


# Adjust columns for rate for a single season
def adjust_for_rate_single_season(season, season_type, totals_save_filename, rate_adjusted_save_filename, rate_column,
                                  rate_factor):
    # Get stats totals for this season
    stats = pd.read_csv(totals_save_filename.format(season, season_type))

    # Get availability of stats
    availability = get_availability(season)

    # Get each available stat type
    stat_types = list(availability.keys())

    # Adjust all stats together for this season
    for stat_type in stat_types:
        if availability[stat_type]:
            # Get box outs and hustle stats
            if stat_type == 'Box Outs' or stat_type == 'Hustle':
                columns_to_adjust = rate_adjusted_columns[stat_type]
                stats[columns_to_adjust] = (stats[columns_to_adjust]
                                            .apply(lambda x: x / (stats[rate_column] * rate_factor), axis=0))

            # Get defensive stats
            elif stat_type == 'Defense':
                for defense_category in defense_categories:
                    columns_to_adjust = rate_adjusted_columns[stat_type][defense_category]
                    stats[columns_to_adjust] = (stats[columns_to_adjust]
                                                .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

            # Get general stats
            elif stat_type == 'General':
                for general_measure_type in general_measure_types:
                    columns_to_adjust = rate_adjusted_columns[stat_type][general_measure_type]
                    stats[columns_to_adjust] = (stats[columns_to_adjust]
                                                .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

            # Get play type stats
            elif stat_type == 'Play Types':
                for play_type, defense in zip(play_types, play_type_defenses):
                    o_columns_to_adjust = rate_adjusted_columns[stat_type][play_type]['offensive']
                    stats[o_columns_to_adjust] = (stats[o_columns_to_adjust]
                                                  .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))
                    if defense:
                        d_columns_to_adjust = rate_adjusted_columns[stat_type][play_type]['defensive']
                        stats[d_columns_to_adjust] = (stats[d_columns_to_adjust]
                                                      .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

            # Get shooting stats
            elif stat_type == 'Shooting':
                for distance_range in distance_ranges:
                    o_columns_to_adjust = rate_adjusted_columns[stat_type][distance_range]['offensive']
                    stats[o_columns_to_adjust] = (stats[o_columns_to_adjust]
                                                  .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

                    d_columns_to_adjust = rate_adjusted_columns[stat_type][distance_range]['defensive']
                    stats[d_columns_to_adjust] = (stats[d_columns_to_adjust]
                                                  .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

            # Get tracking stats
            elif stat_type == 'Tracking':
                for track_type in track_types:
                    columns_to_adjust = rate_adjusted_columns[stat_type][track_type]
                    stats[columns_to_adjust] = (stats[columns_to_adjust]
                                                .apply(lambda x: (x / (stats[rate_column]) * rate_factor), axis=0))

    # Save rate adjusted stats to csv file
    stats.to_csv(rate_adjusted_save_filename.format(season, season_type), index=False)


# Adjust columns for rate for every season
def adjust_for_rate_seasons(seasons, season_types, totals_save_filename, rate_adjusted_save_filename, rate_column,
                            rate_factor):
    # Adjust columns for rate for every season
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            percent_done = ((i * n_season_types + j) /(n_seasons * n_season_types))
            print(f'{percent_done:.2%} {season} {season_type}')

            # Adjust colums for rate for this season
            adjust_for_rate_single_season(season, season_type, totals_save_filename, rate_adjusted_save_filename,
                                          rate_column, rate_factor)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    totals_save_filename = '../Data/SeasonStats/Combined/Totals/{}_{}.csv'
    rate_adjusted_save_filename = '../Data/SeasonStats/Combined/RateAdjusted/{}_{}.csv'
    # combine_stats_seasons(seasons, season_types, totals_save_filename)
    adjust_for_rate_seasons(seasons, season_types, totals_save_filename, rate_adjusted_save_filename, 'POSS', 100)
