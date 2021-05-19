# WEB-project
Creating an online shop, where people can barter their wares.
Note: to load the site well, you have to have an internet connection (to load bootstrap etc.)

Options (all info can be accessed by clicking INFO button on the front page - documentation):
1. Authorizing. You have to sign up to our site to access all functions there.
Use button SIGN UP or LOGIN.
2. Create a post using CREATE A POST button. The form will make you able to enter the description of your wares and photos of your wares
3. You can edit your posts and delete them, using such buttons
4. Every user can comment every post, if he opens a post page (by clicking post id in /index)
Comments can be edited or deleted too
5. You can propose bartering your ware using REPLY button on each post on the front page. That will open you a form for another post, a pair for the original.
Original user can see all replies
6. See and edit your profile data by clicking PROFILE in menu.
7. Search posts in SEARCH tab in header
8. API. 
    + Search post by id → /api/post/<id>
    + Search comments by post_id → /api/comments/<post_id>
    + Search posts by string string → /api/search/<string> (To use different words use _ as delimiter)
Hope that will help    
