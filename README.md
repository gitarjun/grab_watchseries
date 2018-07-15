# grab_watchseries
A Flask application to grab direct download links from "watchseries.to"

Application runs on local machine @ localhost:5000/download

User is greeted with HTML form that expects the link in following example format:
example: https://www1.swatchseries.to/friends/season-1 (My Favorite)

Up on submit AJAX post request will be made to the server and server starts feching direct download links.
After a successful grab user will be serverd with direct download link available for that season
