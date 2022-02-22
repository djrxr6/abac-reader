# abac-reader

Scripts for reading adjudication data from the ABAC website.

### What is ABAC?

*"The ABAC Scheme is the centrepiece of alcohol marketing regulation in Australia.  It is a not for profit organisation established to promote the marketing of alcohol beverages occurring responsibly and consistently with standards of good practice via regulation, education and advice."* (see more on the [ABAC Website](https://www.abac.org.au/about/))

### Purpose of scripts
The scripts in this repository scrape high level information about adjudications on the ABAC website. The intent is to monitor trends in complaints to ABAC, such as the volume of complaints, which sections of the code are being tested and the medium of the marketing communication. 

An early iteration of this code was used to collect data for [this article](https://www.brewsnews.com.au/2021/12/22/complaints-spike-as-abac-judges-major-brands/) on Australian and New Zealand beer industry news website, [Brews News](https://www.brewsnews.com.au/).

This solution does not collect any data from within the adjudication decision files themselves. At this stage there are no plans to do so in the future.

### Again, why?
Yup, this is boring stuff and probably only of interest to only a few people. I began developing this solution, not becuase I saw a wide need for the end output, but simply as a practical way to learn more about the technologies used and to build my portfolio of work.

## Structure / Design
The scripts/commands in this repo are designed to work as follows.
1. Build a list of URLs for each adjudication summary page on the ABAC website (AWK commands)
2. Iterate over the list of URLs to produce a CSV of data from each adjudication page (Python)
3. Perform some tidying/sanitising of the output CSV (AWK script)

I appreciate that the fragmented, multi-step process is not the best solution. However, the initial commands/code I developed were written over approximately two years, with long breaks inbetween coding and no real end goal in mind. I hope to find the time to consolidate the code into one, probably Python, application.

The charts featured in the aforementioned [Brews News Article](https://www.brewsnews.com.au/2021/12/22/complaints-spike-as-abac-judges-major-brands/) were created using PowerBI. Given what I've learned since about Python, [Plotly](https://plotly.com/) and [Dash](https://dash.plotly.com/), it's my hope to integrate these into the solution.

## 1. AWK Commands to build list of URLs

### About these commands

The following test commands are examples of the trial and error I employed to arrive at the end solution to collect the data. I have kept them here for testing and explanatory purposes.

### Adjudication Decision Pages

ABAC adjudications are made available on the ABAC website over multiple pagese. The URL for each page is `https://www.abac.org.au/adjudication/page/<page number>/`, except for the first page which is simply `https://www.abac.org.au/adjudication/`

To see how many pages of decisions exist (how many pages and what the last page number is) use the following command. The example checks for the existence of pages 70 through to 90. (as of 15/12/2021 last page is 80)

`for((i=70;i<=90;i+=1)); do wget --spider -S "https://www.abac.org.au/adjudication/page/$i/" 2>&1 | awk "/HTTP\/|page/{print $1}"; done`

### Individual Adjudication Decisions


First Page (no number in url)

`curl --silent https://www.abac.org.au/adjudication/ | grep adjudication | grep h2`

Other pages (example is page 2)

`curl --silent https://www.abac.org.au/adjudication/page/2 | grep adjudication | grep h2`

### Collect the URL for the decision page, the Name of the product and the date of the decision.

Test on single page and output to console.

`curl --silent https://www.abac.org.au/adjudication/page/2/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">([A-Za-z0-9&\ ]*)<\/a.*date">(.*)<\/p>/\1;\2;\3/'`

### URL only
`curl --silent https://www.abac.org.au/adjudication/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1/'`

Test for multiple pages by looping through a range. Output to console.

`for((i=2;i<=4;i+=1)); do curl --silent https://www.abac.org.au/adjudication/page/$i/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/'; done`

Output to text file

`curl --silent https://www.abac.org.au/adjudication/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/' > abac-adjudications.csv`

`for((i=2;i<=20;i+=1)); do curl --silent https://www.abac.org.au/adjudication/page/$i/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/' >> abac-adjudications.csv; done`

`for((i=21;i<=40;i+=1)); do curl --silent https://www.abac.org.au/adjudication/page/$i/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/' >> abac-adjudications.csv; done`

`for((i=41;i<=60;i+=1)); do curl --silent https://www.abac.org.au/adjudication/page/$i/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/' >> abac-adjudications.csv; done`

`for((i=61;i<=80;i+=1)); do curl --silent https://www.abac.org.au/adjudication/page/$i/ | awk '/adjudication|class="date">./{print $0}' | grep 'h2\|date' | awk 'NR%2{printf "%s ",$0;next;}1' | sed -r 's/.*href="(.*)">(.*)<\/a.*date">(.*)<\/p>/\1;\2;\3/' >> abac-adjudications.csv; done`

### Actual build of input file

