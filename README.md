# Articulate


Articlulate is a Django based application that allows a user to create their articles, favourite other articles. Follow other authors, have a customized feed. It is a place where one may articulate their ideas and present them to the world.

The project revolves around the following ideas:

The webapp will consist of different **Profiles** that will act as *authors* when they write and publish different **Articles** and act as readers otherwise.


Profiles
----------

- A **Profile** has a username, display picture, bio and name.
- Each **Profile** can follow other **Profiles** and *favorite* different **Articles**. 
- All of the authored and the favorited **Articles** will be displayed at a **Profile**'s page. Anyone may switch between authored **articles** and the *favorited* **articles** of a **Profile** by the click of a button. 
- A **Profile** can *author* new **Articles**


Articles
-----------

- Each **Article** has a title, a description, a cover image, the main content in markdown, a publish date and a list of **Tags**.
- Each **Article** can have **Comments** associated to it by different **Profiles**
- Also **Articles** will also have some **Tags** associated to them.
- Any **Profile** that *comments* on an **Article** can delete these. And the *author* of the **Article** can delete all comments if he or she wants to.
- An **Article** can be edited or deleted by the *author*. 
- **Articles** can be *favorited* by **Profiles** and these will be displayed on their own page.
- **Article** page displays a list of recommendations based on the **Tags** used.


Feed
-----------------
- Global feed: That contains all the recent articles and everyone can see these.
- Local feed: A personalized feed for a logged-in **Profile** that contains **Articles** from only the *followed* **Profiles**. These include both the *authored* and the *favorited* **Articles** of the *followed* **Profiles**.
- Both the feeds can be filtered based on **Tags**
- **Articles** can also be searched by using the search bar. A trigram similarity metric checks in title, description for the entered query.
