# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonLinesItemExporter, CsvItemExporter
import pathlib

from ufcStats.utils import print_time

fields_fight_info = [
    'fight_id', 'fighter_1', 'fighter_1_id', 'fighter_2', 'fighter_2_id',
    'winner', 'decision_method', 'fight_duration_lastrnd',
    'fight_duration_lastrnd_time', 'time_format', 'weight_class', 'date',
    'location'
]

fields_fight_stats = [
    'fight_id',
    'fighter_id',
    'fighter_name',
    'fighter_status',
    'kd',
    'n_pass',
    'n_rev',
    'n_sub',
    'sig_str_abs',
    'sig_str_att',
    'sig_str_def',
    'sig_str_land',
    'total_str_abs',
    'total_str_att',
    'total_str_def',
    'total_str_land',
    'td_abs',
    'td_att',
    'td_def',
    'td_land',
    'head_abs',
    'head_att',
    'head_def',
    'head_land',
    'body_abs',
    'body_att',
    'body_def',
    'body_land',
    'leg_abs',
    'leg_att',
    'leg_def',
    'leg_land',
    'distance_abs',
    'distance_att',
    'distance_def',
    'distance_land',
    'clinch_abs',
    'clinch_att',
    'clinch_def',
    'clinch_land',
    'ground_abs',
    'ground_att',
    'ground_def',
    'ground_land',
    'bonus_ko',
    'bonus_sub',
    'bonus_perf',
    'bonus_fight',
    'bonus_belt',
]

fields_fight_rounds = [
    'fight_id',
    'fighter_id',
    'fighter_name',
    'fighter_status',
    'perRoundStatsTotal_fighter1_kd',
    'perRoundStatsTotal_fighter1_sigstr',
    'perRoundStatsTotal_fighter1_sigstrper',
    'perRoundStatsTotal_fighter1_totstr',
    'perRoundStatsTotal_fighter1_td',
    'perRoundStatsTotal_fighter1_tdper',
    'perRoundStatsTotal_fighter1_subatt',
    'perRoundStatsTotal_fighter1_pass',
    'perRoundStatsTotal_fighter1_rev', 
    'perRoundStatsTotal_fighter2_kd', 
    'perRoundStatsTotal_fighter2_sigstr', 
    'perRoundStatsTotal_fighter2_sigstrper',
    'perRoundStatsTotal_fighter2_totstr',
    'perRoundStatsTotal_fighter2_td',
    'perRoundStatsTotal_fighter2_tdper',
    'perRoundStatsTotal_fighter2_subatt',
    'perRoundStatsTotal_fighter2_pass', 
    'perRoundStatsTotal_fighter2_rev', 
    'perRoundStatsSig_fighter1_head',
    'perRoundStatsSig_fighter1_body',
    'perRoundStatsSig_fighter1_leg',
    'perRoundStatsSig_fighter1_distance',
    'perRoundStatsSig_fighter1_clinch',
    'perRoundStatsSig_fighter1_ground',
    'perRoundStatsSig_fighter2_head',
    'perRoundStatsSig_fighter2_body',
    'perRoundStatsSig_fighter2_leg',
    'perRoundStatsSig_fighter2_distance',
    'perRoundStatsSig_fighter2_clinch',
    'perRoundStatsSig_fighter2_ground',
]

class FightSummaryPipeline(object):
    """
    Save Fight level summary to csv file
    """
    def __init__(self):
        self.files = {}

    def open_spider(self, spider):
        time_created = print_time('now')
        # Create directory
        path_fight_info = f'data/fight_info'
        pathlib.Path(path_fight_info).mkdir(parents=True, exist_ok=True)
        # Write to folder
        file = open(f'{path_fight_info}/{time_created}.csv', 'wb')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = fields_fight_info
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class FightStatsPipeline(object):
    """
    Save Fight stats to jl file
    """
    def __init__(self):
        self.files = {}

    def open_spider(self, spider):
        time_created = print_time('now')
        # Create directory
        path_fight_stats = f'data/fight_stats'
        pathlib.Path(path_fight_stats).mkdir(parents=True, exist_ok=True)
        # Write to folder
        file = open(f'{path_fight_stats}/{time_created}.jl', 'wb')
        self.files[spider] = file
        self.exporter = JsonLinesItemExporter(file)
        self.exporter.fields_to_export = fields_fight_stats
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class FightRoundsPipeline(object):
    """
    Save Fight stats to jl file
    """
    def __init__(self):
        self.files = {}

    def open_spider(self, spider):
        time_created = print_time('now')
        # Create directory
        path_fight_rounds = f'data/fight_rounds'
        pathlib.Path(path_fight_rounds).mkdir(parents=True, exist_ok=True)
        # Write to folder
        file = open(f'{path_fight_rounds}/{time_created}.jl', 'wb')
        self.files[spider] = file
        self.exporter = JsonLinesItemExporter(file)
        self.exporter.fields_to_export = fields_fight_rounds
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item