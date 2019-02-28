# Facebook friends export
Actually usable Facebook contact export. No thanks to you, Mark.

![Banner](https://github.com/jankais3r/Facebook-friends-export/raw/master/banner_github.png)


## Dependencies:
```
pip install requests
pip install beautifulsoup4
```

## Steps:
1. Go to `https://facebook.com/<your profile>/friends`
2. Scroll to the bottom of your friends to make sure all of them were dynamically loaded
3. Copy the `<div>` that holds the individual `<li>` elements with your friends' info, like this:
![Save your friends](https://github.com/jankais3r/Facebook-friends-export/raw/master/friends_export.png)
4. Save to `friends_example.html`, run the script

If you have loads of friends, you might get temporarily blocked by Zuck. Increase the sleep duration to make the process slower and less risky.
