from urllib import request
import scrapy

class PLResultsSpider(scrapy.Spider):
    #Spider inits
    name = "results"
    start_urls = ["https://www.skysports.com/premier-league-results"]

    def parse(self, response):
        # yield scrapy.Request("https://bam-cell.nr-data.net/events/1/517f0b291f?a=545304393&v=1216.487a282&to=blcEMUpZCxdYV0MIXVcdJRBLTAoJFlJYDkZbUwoJF1sKCk1GWA1eXEAVSntXCBRcQF4VW1ZcNABLTQkQSndYD0ZLXQoJXUpLFFFE&rst=41126&ck=1&ref=https://www.skysports.com/premier-league-results",callback=self.parseTeams)
        
        matches = response.css("div.fixres__item")

        for match in matches:
            home = match.css("span.swap-text__target::text")[0].get()
            away = match.css("span.swap-text__target::text")[1].get()
            home_score = [int(s) for s in match.css("span.matches__teamscores-side::text")[0].get().split() if s.isdigit()][0]
            away_score = [int(s) for s in match.css("span.matches__teamscores-side::text")[1].get().split() if s.isdigit()][0]

            yield{
                'home': home,
                'away': away,
                'home score': home_score,
                'away score': away_score,
            }

