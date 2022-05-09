import scrapy

class PLTeamsSpider(scrapy.Spider):
    # Spider inits
    name = "teams"
    start_urls = ["https://www.premierleague.com/tables?co=1&se=418&ha=-1&team=FIRST"]

    def parse(self, response):

        #Ensure only first team table is extracted
        table = response.xpath("//div[@data-ui-tab='First Team']")
        #Retrieve list of elements representing teams
        teams = table.xpath("//tr[@data-compseason='418']")

        #Data Tags
        long_name_tag = "span.long::text"
        short_name_tag = "span.short::text"
        points_tag = "td.points::text"

        for team in teams:
            yield{
                'Name': team.css(long_name_tag).get(),
                'Abbreviation': team.css(short_name_tag).get(),
                'Points': team.css(points_tag).get(),
            }


