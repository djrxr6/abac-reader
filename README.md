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
1. 
2. Iterate over the list of URLs to produce a CSV of data from each adjudication page (Python)
3. Perform some tidying/sanitising of the output CSV (AWK script)

I appreciate that the fragmented, multi-step process is not the best solution. However, the initial commands/code I developed were written over approximately two years, with long breaks inbetween coding and no real end goal in mind. I hope to find the time to consolidate the code into one, probably Python, application.

The charts featured in the aforementioned [Brews News Article](https://www.brewsnews.com.au/2021/12/22/complaints-spike-as-abac-judges-major-brands/) were created using PowerBI. Given what I've learned since about Python, [Plotly](https://plotly.com/) and [Dash](https://dash.plotly.com/), it's my hope to integrate these into the solution.


