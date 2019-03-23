#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import codecs
import random
import base64
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

#########################################################################################
#				BEGINNING OF CONFIG SECTION				#
			
# Set your Facebook.com cookies - either by manual copy & paste from Console, or by sniffing a legitimate browser request. I am lazy so I went for the second option.
cookie = "act=15246549%2F6; pnl_data2=cyJhIxvcbxchgvdfghdjkxmjsnmgjhfcIjpmYWxzZSsdfgvnhjztIi9hbGV4YWdfghiZWFudjgnbvcxsdrtQ%3D%3D; x-src=%2Ffriends%7Cpagelet_timeline_app_collection_1055433347%3A2367778758349%3A2; wd=1440x723; c_user=15335354127; fr=1sdgvb8Wlf.AWWi_c8-COsfgdhzvesecAn8.Bb7jGDq.Dm.Fxjy.0.0.Bcd3n1.AfWXkgJn3; xs=132%3AB5OtxYsfdgsgeg%3A2%3A1557765579%3A3071%3A135630; presence=EDvF3EtimeF155434277EuserFA213543354127A2EstateFDutF155135335425305CEchFDp_5f1053435327F0CC; dpr=2; spin=r.48533437_b.trunk_t.155135381_s.1_v.2_; pl=n; sb=KpLsWx8wXafsfsdfhZwZ; locale=en_US; datr=KpLssfdfsBY_i5WpB1_a"

# Set your Facebook username that will be used as a referrer during the crawling process. E.g. https://www.facebook.com/zuck -> zuck
your_username = "zuck"

# Set source file containing the manually extracted list of friends. For help see readme: https://github.com/jankais3r/Facebook-friends-export
friends_extract = file("./friends_example.html", "r")

# Set output file type - possible options are html or tsv. Default: html
export = "html"

# If you wish, you can set a different separator used for the tsv export. Default: \t
separator = "\t"

# Output file name - extension is added automatically based on the selected file type.
output_file =  codecs.open("contacts."+export, mode="w", encoding="utf-8") # for debug use = sys.stdout

# Choose if you want to embed local copies of profile pictures in the HTML report, or if you want to just remotely link them. Image download makes additional http requests, which slightly slows things down. Default: 0
image_download = 0

# If you got blocked in the middle of a run, you can start from where you left off. Just change 0 to the ID of the first non-processed friend. Don't forget to rename the output_file in such case. Default: 0
start_pos = 0

# If you only want to parse the manual friend extract into a nice table without enriching it with any new contact information, set this to 1. To completely eliminate pulling data from Facebook.com, don't forget to set image_download to 0. Default: 0
parse_only = 0

#				  END OF CONFIG SECTION  				#
#########################################################################################

start_time = time.time()

# Start counting from 1 so we get the same number of Friends as Facebook shows
friend_counter = 1

# Workaround for when using commas instead of tabs in the tsv export
if separator == ",":
	sep = "|"
else:
	sep = ","

# Define our Friend properties
class Friend():
	def __init__(self, friend_ID, profile_ID, username, profile_url, picture_url, real_name, other, contact_basic):
		self.friend_ID = friend_ID
		self.profile_ID = profile_ID
		self.username = username
		self.profile_url = profile_url
		self.picture_url = picture_url
		self.real_name = real_name
		self.other = other
		self.contact_basic = contact_basic

# Nice cool and dry place to store your friends
friends = []

friends_extract_parsed = BeautifulSoup(friends_extract, "html.parser")

# Parse individual <LI> tags and extract relevant fields from them
for li in friends_extract_parsed.find_all("li", {"class": "_698"}):
	# Default values
	profile_ID = 0
	username = ""
	profile_url = ""
	picture_url = ""
	real_name = ""
	other = ""
	contact_basic = ""
	
	try:
		picture_url = li.find_all("img")[0]["src"] # The first <IMG> tag contains a profile picture
	except:
		picture_url = "ERROR - investigate"
	
	try:
		profile_ID = li.find_all("a", {"data-profileid": True})[0]["data-profileid"] # The first <A> tag with "data-profileid" property contains a profile id
	except:
		profile_ID =  "ERROR - investigate"
	
	try:
		profile_url_raw = li.find_all("a")[0]["href"] # The first <A> tag contains a profile url and a username (if there is any)
		
		if "profile.php?id=" in profile_url_raw: # Profiles that do not have a username use profile ID instead
			profile_url = profile_url_raw[0:profile_url_raw.find("&")]
			username = ""
		else: # Profiles that have a username
			profile_url = profile_url_raw[0:profile_url_raw.find("?")]
			username = profile_url_raw[profile_url_raw.find("facebook.com/")+13:profile_url_raw.rfind("?")]
	except:
		profile_url =  "ERROR - investigate"
		username =  "ERROR - investigate"
	
	try:
		real_name = li.find_all("a")[2].string # The third <A> tag contains a real name
		other = li.find_all("a")[3].string # The fourth <A> tag can contain various info (number of friends, number of mutual friends, place of work, current city, …)
	except:
		try: # Disabled profiles have slightly different structure
			real_name = li.find_all("a")[1].string # The second <A> tag contains a real name
			other = "" # There is no other info for disabled profiles
		except:
			real_name =  "ERROR - investigate"
			other =  "ERROR - investigate"
	
	# Populate all properties with previously parsed values, except "contact_basic", which is empty at this point and needs to be gathered first
	f = Friend(friend_counter, profile_ID, username, profile_url, picture_url, real_name, other, contact_basic)
	friends.append(f)
	
	friend_counter += 1

if export == "tsv":
	# Print the tsv header row
	print >> output_file, "\"ID\""+separator+"\"Fb Profile ID\""+separator+"\"Fb Username\""+separator+"\"Profile URL\""+separator+"\"Profile Picture URL\""+separator+"\"Real Name\""+separator+"\"Other\""+separator+"\"Basic Info\""

if export == "html":
	# Print the beginning of the HTML document
	print >> output_file, '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset="UTF-8">\n\t\t<title>Facebook Contacts</title>\n\t\t<link rel="stylesheet" type="text/css" href="main.css">\n\t</head>\n\t<body>\n\t\t<div class="limiter">\n\t\t\t<div class="container">\n\t\t\t\t<div style="text-align:center">\n\t\t\t\t\t<table>\n\t\t\t\t\t\t<thead>\n\t\t\t\t\t\t\t<tr><th>ID</th><th>Fb Profile ID</th><th>Fb Username</th><th>Profile URL</th><th>Profile Picture</th><th>Real Name</th><th>Other</th><th>Basic Info</th></tr>\n\t\t\t\t\t\t</thead>\n\t\t\t\t\t\t<tbody>'

# Main cycle for crawling the "contact_basic" property
for i in range(start_pos, len(friends)):
	
	# Skip friends with disabled profiles
	if friends[i].profile_url != "":
		
		# If we only want to parse the manual friend extract into a nice table, we can skip the request part.
		if parse_only == 0:
			
			# Wait 4-9 seconds before each request. Protection against "You’re Temporarily Blocked - It looks like you were misusing this feature by going too fast. You’ve been blocked from using it."
			time.sleep(random.randint(40, 90)/10)
				
			# Set the correct profile URL with username/profile ID
			if friends[i].username == "":
				about_url = friends[i].profile_url+"&sk=about" #&section=contact-info
			else:
				about_url = friends[i].profile_url+"/about" #?section=contact-info
			
			# Request the About page
			r = requests.get(
				about_url, 
				headers={
					"Cookie": cookie, 
					"Accept": "*/*", 
					"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15", 
					"Accept-Language": "en-us", 
					"Referer": "https://www.facebook.com/"+your_username+"/friends", 
					"DNT": "1"
				}
			)
			
			if "You’re Temporarily Blocked" in r.text:
				print "We got blocked by Facebook. Aborting. Try again later, maybe with increased sleep() values."
				if export == "html":
					print >> output_file, '\t\t\t\t\t\t</tbody>\n\t\t\t\t\t</table><a style="color: #ffffff" href="https://twitter.com/hashtag/deletefacebook?f=live" target="_blank">#deleteFacebook</a>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t</body>\n</html>'
				output_file.close()
				quit()
			
			# The Facebook.com source is intentionally obfuscated to make parsing it more difficult. This little change makes it parsable again.
			unfuck = r.text.replace("<code", "<div").replace("</code", "</div").replace("!--", "").replace("-->", "")
			unfuck_parsed = BeautifulSoup(unfuck, "html.parser")
			
			# Facebook poisons all non-email links with their tracking domain https://l.facebook.com/l.php?u=. Let's fix that.
			for a in unfuck_parsed.find_all("a"):
				if "instagram.com" in a["href"] and "instagram.com" not in a.text:
					a["href"] = "https://instagram.com/"+a.text
				if "mailto:" not in a["href"] and "https://instagram.com/" not in a["href"]:
					a["href"] = a.text
			
			# Pulling the <UL> element with our basic info
			try:
				basic_info = unfuck_parsed.find_all("ul", {"data-overviewsection": "contact_basic"})[0]
			except:
				basic_info =  "ERROR - investigate"
			
			friends[i].contact_basic = basic_info.encode("utf8").replace("(", " (")
	
	# Creates and populates new row for every friend
	if export == "tsv":
		print >> output_file, "\""+str(friends[i].friend_ID)+"\""+separator+"\""+str(friends[i].profile_ID)+"\""+separator+"\""+friends[i].username+"\""+separator+"\""+friends[i].profile_url+"\""+separator+"\""+friends[i].picture_url+"\""+separator+"\""+friends[i].real_name+"\""+separator+"\""+friends[i].other+"\""+separator+"\""+(u""+sep.join(list(basic_info.strings)).encode('utf-8') if (friends[i].profile_url != "" and parse_only == 0) else "")+"\""
		
	if export == "html":
		
		if image_download == 1:
			# Wait 0.5-1 second before each request. Protection against "You’re Temporarily Blocked - It looks like you were misusing this feature by going too fast. You’ve been blocked from using it."
			time.sleep(random.randint(5,10)/10)
			
			# Let's download those images and encode them as base64 so our archive is not dependent on Mark
			r = requests.get(
				friends[i].picture_url, 
				headers={
					"Accept": "image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5", 
					"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15", 
					"Accept-Language": "en-us", 
					"Referer": "https://www.facebook.com/"+your_username+"/friends", 
					"DNT": "1"
				}
			)
		
		# Creates and populates new HTML table row for every friend	
		print >> output_file, "\t\t\t\t\t\t\t<tr><td>"+str(friends[i].friend_ID)+"</td><td>"+str(friends[i].profile_ID)+"</td><td>"+friends[i].username+"</td><td><a href=\""+friends[i].profile_url+"\">"+friends[i].profile_url+"</a></td><td><img src=\""+("data:image/jpg;base64,"+base64.b64encode(r.content) if image_download == 1 else friends[i].picture_url)+"\" width=\"50\"></td><td>"+friends[i].real_name+"</td><td>"+friends[i].other+"</td><td>"+friends[i].contact_basic+"</td></tr>"
	
	print "Processed friend "+str(friends[i].friend_ID)+" of "+str(len(friends))+"."
	
# Print the end of the final HTML document
if export == "html":
	print >> output_file, '\t\t\t\t\t\t</tbody>\n\t\t\t\t\t</table><a style="color: #ffffff" href="https://twitter.com/hashtag/deletefacebook?f=live" target="_blank">#deleteFacebook</a>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t</body>\n</html>'

output_file.close()
end_time = time.time()
print "Done. It took "+str(round((end_time-start_time),0))[0:-2]+"s. Results saved to "+output_file.name+"."
