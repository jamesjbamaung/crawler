import scrapy
from scrapy.loader import ItemLoader
from ufcStats.items import *
from ufcStats.utils import *


class FightsSpider(scrapy.Spider):
    name = 'ufcFights'
    start_urls = ['http://ufcstats.com/statistics/events/completed?page=all']

    custom_settings = {
        'ITEM_PIPELINES': {
            'ufcStats.pipelines.FightSummaryPipeline': 400,
            'ufcStats.pipelines.FightStatsPipeline': 410,
            'ufcStats.pipelines.FightRoundsPipeline': 420
        }
    }

    def parse(self, response):
        """
        Parse the event listing page, follow link to individual events page
        """

        events_url = response.css(
            'tbody .b-statistics__table-row ::attr(href)')

        for event in events_url:
            yield response.follow(event, callback=self.parse_event_link)

    def parse_event_link(self, response):
        """
        Parse the event page, follow link to each individual fight page
        """

        event_info = response.css('.b-list__box-list-item')
        date = event_info[0].css('::text').getall()[-1]
        location = event_info[1].css('::text').getall()[-1]
        fights_url = response.css(
            '.b-fight-details__table-row ::attr(data-link)')

        for fight in fights_url:
            yield response.follow(fight,
                                  callback=self.parse_fight_info,
                                  cb_kwargs=dict(date=date, location=location))

    def parse_fight_info(self, response, date, location):
        """
        Parse fight info - fight level summary, and fighter stats
        """

        ##### Fight summary ######
        fight_id = response.url.split('/')[-1]
        # date and location carry over from events page
        date = date.strip()
        location = location.strip()

        status = response.css(
            '.b-fight-details__person-status ::text').getall()

        # Fighter names
        names = response.css(
            '.b-fight-details__person-name :not(p)::text').getall()
        try:
            fighter_1 = names[0].strip()
            fighter_2 = names[1].strip()
        except:
            fighter_1 = None
            fighter_2 = None

        # IDs - Handle errors due to missing fighter link
        ids = response.css('.b-fight-details__person-name')
        fighter_1_id = ids[0].css('::attr(href)').get()
        fighter_2_id = ids[1].css('::attr(href)').get()

        if fighter_1_id is not None:
            fighter_1_id = fighter_1_id.split('/')[-1]
        if fighter_2_id is not None:
            fighter_2_id = fighter_2_id.split('/')[-1]

        # Winner name
        if status[0].strip() == 'W':
            winner = fighter_1
        elif status[1].strip() == 'W':
            winner = fighter_2
        elif status[0].strip() == 'D':
            winner = 'Draw'
        else:
            winner = 'NC'

        weight_class = response.css(
            '.b-fight-details__fight-title ::text').getall()

        if len(weight_class) > 1:
            weight_class = weight_class[-1].strip()
        if len(weight_class) == 1:
            weight_class = weight_class[0].strip()

        decision_method = response.css(
            "i.b-fight-details__text-item_first [style='font-style: normal'] ::text"
        ).get()

        fight_details = response.css('.b-fight-details__text-item')

        time_format = fight_details[2].css('::text').getall()[-1]
        fight_duration_lastrnd = fight_details[0].css('::text').getall()[-1]
        fight_duration_lastrnd_time = fight_details[1].css(
            '::text').getall()[-1]

        l = ItemLoader(item=FightsItem(), response=response)
        l.add_value('fight_id', fight_id)
        l.add_value('date', date)
        l.add_value('location', location)
        l.add_value('fighter_1', fighter_1)
        l.add_value('fighter_1_id', fighter_1_id)
        l.add_value('fighter_2', fighter_2)
        l.add_value('fighter_2_id', fighter_2_id)
        l.add_value('winner', winner)
        l.add_value('weight_class', weight_class)
        l.add_value('decision_method', decision_method.strip())
        l.add_value('time_format', time_format.strip())
        l.add_value('fight_duration_lastrnd', fight_duration_lastrnd.strip())
        l.add_value('fight_duration_lastrnd_time',
                    fight_duration_lastrnd_time.strip())


        #adding bonuses
        bonus = response.css('.b-fight-details__fight-title img::attr(src)').extract()
        bonus_type = ''
        bonus_type2 = ''
        bonus_type3 = ''

        bonus_ko = 0
        bonus_sub = 0
        bonus_perf = 0
        bonus_fight = 0
        bonus_belt = 0
        
        if len(bonus) > 2:
            bonus_start = bonus[0].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[0].find('.png')
            bonus_type = bonus[0][bonus_start:bonus_end]       

            bonus_start = bonus[1].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[1].find('.png')
            bonus_type2 = bonus[1][bonus_start:bonus_end]  

            bonus_start = bonus[2].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[2].find('.png')
            bonus_type3 = bonus[2][bonus_start:bonus_end]  
        elif len(bonus) > 1:
            bonus_start = bonus[0].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[0].find('.png')
            bonus_type = bonus[0][bonus_start:bonus_end]       

            bonus_start = bonus[1].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[1].find('.png')
            bonus_type2 = bonus[1][bonus_start:bonus_end]      

        elif len(bonus) > 0:
            bonus_start = bonus[0].find('.com/')
            bonus_start = bonus_start + 5
            bonus_end = bonus[0].find('.png')
            bonus_type = bonus[0][bonus_start:bonus_end]
        
        if bonus_type == 'ko' or bonus_type2 == 'ko' or bonus_type3 == 'ko':
            bonus_ko = 1
        if bonus_type == 'sub' or bonus_type2 == 'sub' or bonus_type3 == 'sub':
            bonus_sub = 1
        if bonus_type == 'perf' or bonus_type2 == 'perf' or bonus_type3 == 'perf':
            bonus_perf = 1
        if bonus_type == 'fight' or bonus_type2 == 'fight' or bonus_type3 == 'fight':
            bonus_fight = 1
        if bonus_type == 'belt' or bonus_type2 == 'belt' or bonus_type3 == 'belt':
            bonus_belt = 1

        l.add_value('bonus_ko', bonus_ko)
        l.add_value('bonus_sub', bonus_sub)
        l.add_value('bonus_perf', bonus_perf)
        l.add_value('bonus_fight', bonus_fight)
        l.add_value('bonus_belt', bonus_belt)




        
        #populating per round stats
        perRoundStats = response.css('.js-fight-table')
        if(len(perRoundStats) == 2):

            perRoundStatsTotal = perRoundStats[0].css('tbody .b-fight-details__table-col:not(.l-page_align_left) p ::text').getall()
            perRoundStatsSig = perRoundStats[1].css('tbody .b-fight-details__table-col:not(.l-page_align_left) p ::text').getall()

            perRoundStatsTotal= [i.strip() for i in perRoundStatsTotal]
            perRoundStatsSig = [i.strip() for i in perRoundStatsSig]

            perRoundStatsTotal_fighter1 = []
            perRoundStatsTotal_fighter2 = []
            i = 0
            j = 1
            while i < len(perRoundStatsTotal):
                perRoundStatsTotal_fighter1.append(perRoundStatsTotal[i])
                i += 2

            while j < len(perRoundStatsTotal):
                perRoundStatsTotal_fighter2.append(perRoundStatsTotal[j])
                j += 2

            perRoundStatsSig_fighter1 = []
            perRoundStatsSig_fighter2 = []
            i = 0
            j = 1
            while i < len(perRoundStatsSig):
                perRoundStatsSig_fighter1.append(perRoundStatsSig[i])
                i += 2

            while j < len(perRoundStatsSig):
                perRoundStatsSig_fighter2.append(perRoundStatsSig[j])
                j += 2
            
            roundCounter = 0

            perRoundStatsTotal_fighter1_kd = []
            perRoundStatsTotal_fighter1_sigstr = []
            perRoundStatsTotal_fighter1_sigstrper = []
            perRoundStatsTotal_fighter1_totstr = []
            perRoundStatsTotal_fighter1_td = []
            perRoundStatsTotal_fighter1_tdper = []
            perRoundStatsTotal_fighter1_subatt = []
            perRoundStatsTotal_fighter1_pass = []
            perRoundStatsTotal_fighter1_rev = []

            perRoundStatsTotal_fighter2_kd = []
            perRoundStatsTotal_fighter2_sigstr = []
            perRoundStatsTotal_fighter2_sigstrper = []
            perRoundStatsTotal_fighter2_totstr = []
            perRoundStatsTotal_fighter2_td = []
            perRoundStatsTotal_fighter2_tdper = []
            perRoundStatsTotal_fighter2_subatt = []
            perRoundStatsTotal_fighter2_pass = []
            perRoundStatsTotal_fighter2_rev = []

            while roundCounter < len(perRoundStatsTotal_fighter1):
                #kd
                perRoundStatsTotal_fighter1_kd.append(int(perRoundStatsTotal_fighter1[roundCounter]))
                perRoundStatsTotal_fighter2_kd.append(int(perRoundStatsTotal_fighter2[roundCounter]))

                #significant strikes
                a = perRoundStatsTotal_fighter1[roundCounter+1].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter1_sigstr.append(a)
                a = perRoundStatsTotal_fighter2[roundCounter+1].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter2_sigstr.append(a)

                #significant strike percentage
                x = perRoundStatsTotal_fighter1[roundCounter+2].strip('%')
                perRoundStatsTotal_fighter1_sigstrper.append(int(x))
                x = perRoundStatsTotal_fighter2[roundCounter+2].strip('%')
                perRoundStatsTotal_fighter2_sigstrper.append(int(x))

                #total strikes
                a = perRoundStatsTotal_fighter1[roundCounter+3].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter1_totstr.append(a)
                a = perRoundStatsTotal_fighter2[roundCounter+3].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter2_totstr.append(a)

                #take downs
                a = perRoundStatsTotal_fighter1[roundCounter+4].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter1_td.append(a)
                a = perRoundStatsTotal_fighter2[roundCounter+4].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsTotal_fighter2_td.append(a)

                #takedown percentage
                x = perRoundStatsTotal_fighter1[roundCounter+5].strip('%')
                perRoundStatsTotal_fighter1_tdper.append(int(x))
                x = perRoundStatsTotal_fighter2[roundCounter+5].strip('%')
                perRoundStatsTotal_fighter2_tdper.append(int(x))

                #submission attempt
                perRoundStatsTotal_fighter1_subatt.append(int(perRoundStatsTotal_fighter1[roundCounter+6]))
                perRoundStatsTotal_fighter2_subatt.append(int(perRoundStatsTotal_fighter2[roundCounter+6]))

                #pass
                perRoundStatsTotal_fighter1_pass.append(int(perRoundStatsTotal_fighter1[roundCounter+7]))
                perRoundStatsTotal_fighter2_pass.append(int(perRoundStatsTotal_fighter2[roundCounter+7]))

                #reversal
                perRoundStatsTotal_fighter1_rev.append(int(perRoundStatsTotal_fighter1[roundCounter+8]))
                perRoundStatsTotal_fighter2_rev.append(int(perRoundStatsTotal_fighter2[roundCounter+8]))

                roundCounter += 9
            
            roundCounter_sig = 0
            perRoundStatsSig_fighter1_head = []
            perRoundStatsSig_fighter1_body = []
            perRoundStatsSig_fighter1_leg = []
            perRoundStatsSig_fighter1_distance = []
            perRoundStatsSig_fighter1_clinch = []
            perRoundStatsSig_fighter1_ground = []
            perRoundStatsSig_fighter2_head = []
            perRoundStatsSig_fighter2_body = []
            perRoundStatsSig_fighter2_leg = []
            perRoundStatsSig_fighter2_distance = []
            perRoundStatsSig_fighter2_clinch = []
            perRoundStatsSig_fighter2_ground = []

            while roundCounter_sig < len(perRoundStatsSig_fighter1):
                #head
                a = perRoundStatsSig_fighter1[roundCounter_sig+2].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_head.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+2].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_head.append(a)
                #body
                a = perRoundStatsSig_fighter1[roundCounter_sig+3].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_body.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+3].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_body.append(a)
                #leg
                a = perRoundStatsSig_fighter1[roundCounter_sig+4].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_leg.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+4].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_leg.append(a)
                #distance
                a = perRoundStatsSig_fighter1[roundCounter_sig+5].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_distance.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+5].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_distance.append(a)
                #clinch
                a = perRoundStatsSig_fighter1[roundCounter_sig+6].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_clinch.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+6].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_clinch.append(a)
                #ground
                a = perRoundStatsSig_fighter1[roundCounter_sig+7].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter1_ground.append(a)
                a = perRoundStatsSig_fighter2[roundCounter_sig+7].split(' of ')
                a = [int(b) for b in a]
                perRoundStatsSig_fighter2_ground.append(a)

                roundCounter_sig += 8



        else:
            perRoundStatsTotal_fighter1_kd = []
            perRoundStatsTotal_fighter1_sigstr = []
            perRoundStatsTotal_fighter1_sigstrper = []
            perRoundStatsTotal_fighter1_totstr = []
            perRoundStatsTotal_fighter1_td = []
            perRoundStatsTotal_fighter1_tdper = []
            perRoundStatsTotal_fighter1_subatt = []
            perRoundStatsTotal_fighter1_pass = []
            perRoundStatsTotal_fighter1_rev = []
            perRoundStatsTotal_fighter2_kd = []
            perRoundStatsTotal_fighter2_sigstr = []
            perRoundStatsTotal_fighter2_sigstrper = []
            perRoundStatsTotal_fighter2_totstr = []
            perRoundStatsTotal_fighter2_td = []
            perRoundStatsTotal_fighter2_tdper = []
            perRoundStatsTotal_fighter2_subatt = []
            perRoundStatsTotal_fighter2_pass = []
            perRoundStatsTotal_fighter2_rev = []
            perRoundStatsSig_fighter1_head = []
            perRoundStatsSig_fighter1_body = []
            perRoundStatsSig_fighter1_leg = []
            perRoundStatsSig_fighter1_distance = []
            perRoundStatsSig_fighter1_clinch = []
            perRoundStatsSig_fighter1_ground = []
            perRoundStatsSig_fighter2_head = []
            perRoundStatsSig_fighter2_body = []
            perRoundStatsSig_fighter2_leg = []
            perRoundStatsSig_fighter2_distance = []
            perRoundStatsSig_fighter2_clinch = []
            perRoundStatsSig_fighter2_ground = []

        l.add_value('perRoundStatsTotal_fighter1_kd', perRoundStatsTotal_fighter1_kd)
        l.add_value('perRoundStatsTotal_fighter1_sigstr', perRoundStatsTotal_fighter1_sigstr)
        l.add_value('perRoundStatsTotal_fighter1_sigstrper', perRoundStatsTotal_fighter1_sigstrper)
        l.add_value('perRoundStatsTotal_fighter1_totstr', perRoundStatsTotal_fighter1_totstr)
        l.add_value('perRoundStatsTotal_fighter1_td', perRoundStatsTotal_fighter1_td)
        l.add_value('perRoundStatsTotal_fighter1_tdper', perRoundStatsTotal_fighter1_tdper)
        l.add_value('perRoundStatsTotal_fighter1_subatt', perRoundStatsTotal_fighter1_subatt)
        l.add_value('perRoundStatsTotal_fighter1_pass', perRoundStatsTotal_fighter1_pass)
        l.add_value('perRoundStatsTotal_fighter1_rev', perRoundStatsTotal_fighter1_rev)
        l.add_value('perRoundStatsTotal_fighter2_kd', perRoundStatsTotal_fighter2_kd)
        l.add_value('perRoundStatsTotal_fighter2_sigstr', perRoundStatsTotal_fighter2_sigstr)
        l.add_value('perRoundStatsTotal_fighter2_sigstrper', perRoundStatsTotal_fighter2_sigstrper)
        l.add_value('perRoundStatsTotal_fighter2_totstr', perRoundStatsTotal_fighter2_totstr)
        l.add_value('perRoundStatsTotal_fighter2_td', perRoundStatsTotal_fighter2_td)
        l.add_value('perRoundStatsTotal_fighter2_tdper', perRoundStatsTotal_fighter2_tdper)
        l.add_value('perRoundStatsTotal_fighter2_subatt', perRoundStatsTotal_fighter2_subatt)
        l.add_value('perRoundStatsTotal_fighter2_pass', perRoundStatsTotal_fighter2_pass)
        l.add_value('perRoundStatsTotal_fighter2_rev', perRoundStatsTotal_fighter2_rev)
        l.add_value('perRoundStatsSig_fighter1_head', perRoundStatsSig_fighter1_head)
        l.add_value('perRoundStatsSig_fighter1_body', perRoundStatsSig_fighter1_body)
        l.add_value('perRoundStatsSig_fighter1_leg', perRoundStatsSig_fighter1_leg)
        l.add_value('perRoundStatsSig_fighter1_distance', perRoundStatsSig_fighter1_distance)
        l.add_value('perRoundStatsSig_fighter1_clinch', perRoundStatsSig_fighter1_clinch)
        l.add_value('perRoundStatsSig_fighter1_ground', perRoundStatsSig_fighter1_ground)
        l.add_value('perRoundStatsSig_fighter2_head', perRoundStatsSig_fighter2_head)
        l.add_value('perRoundStatsSig_fighter2_body', perRoundStatsSig_fighter2_body)
        l.add_value('perRoundStatsSig_fighter2_leg', perRoundStatsSig_fighter2_leg)
        l.add_value('perRoundStatsSig_fighter2_distance', perRoundStatsSig_fighter2_distance)
        l.add_value('perRoundStatsSig_fighter2_clinch', perRoundStatsSig_fighter2_clinch)
        l.add_value('perRoundStatsSig_fighter2_ground', perRoundStatsSig_fighter2_ground)

        # stripTest = perRoundStatsTotal[1].css('p ::text').getall()
        # landedBy = response.css('.b-fight-details__charts-table')
        # byTargetArray = landedBy[0].css('.b-fight-details__charts-row i ::text').getall()

        # byPositionArray = landedBy[1].css('.b-fight-details__charts-row i ::text').getall()

        # byTargetArray= [i.strip() for i in byTargetArray]
        # byPositionArray= [i.strip() for i in byPositionArray]







        ##### Fighter Stats ######
        fighter_status = [i.strip() for i in status]
        fighter_id = list([fighter_1_id, fighter_2_id])
        fighter_name = list([fighter_1, fighter_2])

        stats = response.css('table:not(.js-fight-table)')

        # Fight stats - handle missing values
        if len(stats) == 2:
            stats_total = stats[0].css(
                '.b-fight-details__table-body .b-fight-details__table-col')
            stats_str = stats[1].css(
                '.b-fight-details__table-body .b-fight-details__table-col')

            ## Totals
            kd = stats_total[1].css('p ::text').getall()
            kd = [int(i.strip()) for i in kd]

            sig_str = stats_total[2].css('p ::text').getall()
            total_str = stats_total[4].css('p ::text').getall()
            td = stats_total[5].css('p ::text').getall()

            n_sub = stats_total[7].css('p ::text').getall()
            n_sub = [int(i.strip()) for i in n_sub]

            n_pass = stats_total[8].css('p ::text').getall()
            n_pass = [int(i.strip()) for i in n_pass]

            n_rev = stats_total[9].css('p ::text').getall()
            n_rev = [int(i.strip()) for i in n_rev]

            ## Significant strikes
            head = stats_str[3].css('p ::text').getall()
            body = stats_str[4].css('p ::text').getall()
            leg = stats_str[5].css('p ::text').getall()
            distance = stats_str[6].css('p ::text').getall()
            clinch = stats_str[7].css('p ::text').getall()
            ground = stats_str[8].css('p ::text').getall()
        else:
            kd = None
            sig_str = None
            total_str = None
            td = None
            n_sub = None
            n_pass = None
            n_rev = None
            head = None
            body = None
            leg = None
            distance = None
            clinch = None
            ground = None

        #l.add_value('fight_id', fight_id)
        l.add_value('fighter_id', fighter_id)
        l.add_value('fighter_name', fighter_name)
        l.add_value('fighter_status', fighter_status)
        l.add_value('kd', kd)
        l.add_value('sig_str_land', get_element_atk(sig_str, 'landed'))
        l.add_value('sig_str_att', get_element_atk(sig_str, 'attempt'))
        l.add_value('total_str_land', get_element_atk(total_str, 'landed'))
        l.add_value('total_str_att', get_element_atk(total_str, 'attempt'))
        l.add_value('td_land', get_element_atk(td, 'landed'))
        l.add_value('td_att', get_element_atk(td, 'attempt'))
        l.add_value('n_sub', n_sub)
        l.add_value('n_pass', n_pass)
        l.add_value('n_rev', n_rev)
        l.add_value('head_land', get_element_atk(head, 'landed'))
        l.add_value('head_att', get_element_atk(head, 'attempt'))
        l.add_value('body_land', get_element_atk(body, 'landed'))
        l.add_value('body_att', get_element_atk(body, 'attempt'))
        l.add_value('leg_land', get_element_atk(leg, 'landed'))
        l.add_value('leg_att', get_element_atk(leg, 'attempt'))
        l.add_value('distance_land', get_element_atk(distance, 'landed'))
        l.add_value('distance_att', get_element_atk(distance, 'attempt'))
        l.add_value('clinch_land', get_element_atk(clinch, 'landed'))
        l.add_value('clinch_att', get_element_atk(clinch, 'attempt'))
        l.add_value('ground_land', get_element_atk(ground, 'landed'))
        l.add_value('ground_att', get_element_atk(ground, 'attempt'))
        l.add_value('sig_str_abs', get_element_dmg(sig_str, 'absorbed'))
        l.add_value('sig_str_def', get_element_dmg(sig_str, 'defended'))
        l.add_value('total_str_abs', get_element_dmg(total_str, 'absorbed'))
        l.add_value('total_str_def', get_element_dmg(total_str, 'defended'))
        l.add_value('td_abs', get_element_dmg(td, 'absorbed'))
        l.add_value('td_def', get_element_dmg(td, 'defended'))
        l.add_value('head_abs', get_element_dmg(head, 'absorbed'))
        l.add_value('head_def', get_element_dmg(head, 'defended'))
        l.add_value('body_abs', get_element_dmg(body, 'absorbed'))
        l.add_value('body_def', get_element_dmg(body, 'defended'))
        l.add_value('leg_abs', get_element_dmg(leg, 'absorbed'))
        l.add_value('leg_def', get_element_dmg(leg, 'defended'))
        l.add_value('distance_abs', get_element_dmg(distance, 'absorbed'))
        l.add_value('distance_def', get_element_dmg(distance, 'defended'))
        l.add_value('clinch_abs', get_element_dmg(clinch, 'absorbed'))
        l.add_value('clinch_def', get_element_dmg(clinch, 'defended'))
        l.add_value('ground_abs', get_element_dmg(ground, 'absorbed'))
        l.add_value('ground_def', get_element_dmg(ground, 'defended'))
        print('adding fight stats')
        yield l.load_item()


class FightersSpider(scrapy.Spider):
    name = 'ufcFighters'
    start_urls = ['http://ufcstats.com/statistics/fighters']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/fighter_stats/%(time)s.csv'
    }

    def parse(self, response):
        """
        Parse the fighter listing page, follow link to each alphabetical page
        """

        by_alphabets = response.css(
            '.b-statistics__nav-link ::attr(href)').getall()

        pages_by_alphabets = []
        for alphabet in by_alphabets:
            link = alphabet + '&page=all'
            pages_by_alphabets.append(link)

        for page in pages_by_alphabets:
            yield response.follow(page, callback=self.parse_fighter_link)

    def parse_fighter_link(self, response):
        """
        Parse each alphabetical listing, find links to each fighter
        """

        rows = response.css('tbody .b-statistics__table-row')
        rows.pop(0)

        for row in rows:
            fighter_link = row.css('.b-statistics__table-col ::attr(href)').get()
            yield response.follow(fighter_link, callback=self.parse_fighter_stat)

    def parse_fighter_stat(self, response):
        """
        Parse fighter summary stats
        """
        fighter_id = response.url.split('/')[-1]
        name = response.css('.b-content__title-highlight ::text').get()

        record = response.css('.b-content__title-record ::text').get()
        record = re.findall(r'[0-9]+', record)

        stat_box = response.css('.b-list__box-list')
        stat_box_1 = stat_box[0].css('.b-list__box-list-item')
        stat_box_2 = stat_box[1].css('.b-list__box-list-item')
        stat_box_3 = stat_box[2].css('.b-list__box-list-item')

        height = stat_box_1[0].css('li::text').getall()
        weight = stat_box_1[1].css('li::text').getall()
        reach = stat_box_1[2].css('li::text').getall()
        stance = stat_box_1[3].css('li::text').getall()
        dob = stat_box_1[4].css('li::text').getall()

        sig_str_land_pM = stat_box_2[0].css('li::text').getall()
        sig_str_land_pct = stat_box_2[1].css('li::text').getall()
        sig_str_abs_pM = stat_box_2[2].css('li::text').getall()
        sig_str_def_pct = stat_box_2[3].css('li::text').getall()
        td_avg = stat_box_3[1].css('li::text').getall()
        td_land_pct = stat_box_3[2].css('li::text').getall()
        td_def_pct = stat_box_3[3].css('li::text').getall()
        sub_avg = stat_box_3[4].css('li::text').getall()

        l = ItemLoader(item=FighterSummaryItem(), response=response)
        l.add_value('fighter_id', fighter_id)
        l.add_value('name', name.strip())
        l.add_value('height', height[1].strip())
        l.add_value('weight', weight[1].strip())
        l.add_value('reach', reach[1].strip())
        l.add_value('stance', stance[1].strip())
        l.add_value('dob', dob[1].strip())
        l.add_value('n_win', record[0])
        l.add_value('n_loss', record[1])
        l.add_value('n_draw', record[2])
        l.add_value('sig_str_land_pM', sig_str_land_pM[1].strip())
        l.add_value('sig_str_land_pct', sig_str_land_pct[1].strip())
        l.add_value('sig_str_abs_pM', sig_str_abs_pM[1].strip())
        l.add_value('sig_str_def_pct', sig_str_def_pct[1].strip())
        l.add_value('td_avg', td_avg[1].strip())
        l.add_value('td_land_pct', td_land_pct[1].strip())
        l.add_value('td_def_pct', td_def_pct[1].strip())
        l.add_value('sub_avg', sub_avg[1].strip())
        print('adding fight')
        yield l.load_item()


class UpcomingFightsSpider(scrapy.Spider):
    name = 'upcoming'
    start_urls = ['http://ufcstats.com/statistics/events/completed']
    time_created = print_time('now')

    custom_settings = {
        'FEED_FORMAT': 'csv', 
        'FEED_URI': f'data/upcoming/{time_created}.csv'
    }

    def parse(self, response):
        """
        Parse the event listing page, follow link to individual events page
        """

        event_url = response.css(
            'tbody .b-statistics__table-row_type_first ::attr(href)').get()

        yield response.follow(event_url, callback=self.parse_upcoming_event)

    def parse_upcoming_event(self, response):
        """
        Parse the event page, follow link to each individual fight page
        """

        event_info = response.css('.b-list__box-list-item')
        date = event_info[0].css('::text').getall()[-1]
        location = event_info[1].css('::text').getall()[-1]
        fights_url = response.css(
            '.b-fight-details__table-row ::attr(data-link)')

        for fight in fights_url:
            yield response.follow(fight,
                                  callback=self.parse_upcoming_fight,
                                  cb_kwargs=dict(date=date, location=location))

    def parse_upcoming_fight(self, response, date, location):
        """
        Parse fight info - fight level summary, and fighter stats
        """

        ##### Fight summary ######
        fight_id = response.url.split('/')[-1]
        # date and location carry over from events page
        date = date.strip()
        location = location.strip()

        # Fighter names
        names = response.css(
            '.b-fight-details__person-name :not(p)::text').getall()
        try:
            fighter_1 = names[0].strip()
            fighter_2 = names[1].strip()
        except:
            fighter_1 = None
            fighter_2 = None

        # IDs - Handle errors due to missing fighter link
        ids = response.css('.b-fight-details__person-name')
        fighter_1_id = ids[0].css('::attr(href)').get()
        fighter_2_id = ids[1].css('::attr(href)').get()

        if fighter_1_id is not None:
            fighter_1_id = fighter_1_id.split('/')[-1]
        if fighter_2_id is not None:
            fighter_2_id = fighter_2_id.split('/')[-1]

        weight_class = response.css(
            '.b-fight-details__fight-title ::text').getall()

        if len(weight_class) > 1:
            weight_class = weight_class[-1].strip()
        if len(weight_class) == 1:
            weight_class = weight_class[0].strip()

        l = ItemLoader(item=UpcomingFightsItem(), response=response)
        l.add_value('fight_id', fight_id)
        l.add_value('date', date)
        l.add_value('location', location)
        l.add_value('fighter_1', fighter_1)
        l.add_value('fighter_1_id', fighter_1_id)
        l.add_value('fighter_2', fighter_2)
        l.add_value('fighter_2_id', fighter_2_id)
        l.add_value('weight_class', weight_class)

        yield l.load_item()