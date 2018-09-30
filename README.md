# dum-generic
A modern MU* engine

## What is it?
DUM is a hobby project attempting to develop a feature-rich Python codebase for a MUD style game. It is building on brillinat work by Mark Frimston, be sure to check out his Mud-Pi project (https://github.com/Frimkron/mud-pi).

> Note: A **dev server** running `dum-generic` has been deployed! Feel free to get in touch via email (bartek.radwanski@gmail.com) if you'd like to try it out!

## Features
Check out http://dumengine.wikidot.com/dum-v0-1-feature-summary for a longer description of currently implemented features. The Wiki page will hopefully help you understand how certain things have been designed. I did try my best to comment the code in a coherent manner, many comments come from the original project by Mark Frimston - I would highly recommend familiarising yourself with his work (https://github.com/Frimkron/mud-pi) for improved understanding of basic design decisions I have expanded on. In summary following concepts have so far been implemented:
* Rooms
* Player chat
* NPCs
* Basic inventory, character sheet and items
* Environmental actors
* PvE and PvP combat
* Database
* Player authentication
* 256 ANSI color support on compatible MUD clients

## Running the Server
Any environment capable of running Python3 + MySQL will do. My own development environment is as follows:
- Google Cloud Instance running Ubuntu 18.04.1 LTS
- Python3 3.6.5-3ubuntu1
- Mysql-server 5.7.23-0ubuntu0.18.04.1

Simplified steps to get things up and running are as follows. Somewhere down my TODO list is asome sort of an automated batch, which would install all the prerequisites, set up the database etc. I'm always happy to help if you need a hand or get stuck at any point.

1. Install python3
2. Install and configure MySQL instance  (Or SQLite https://www.sqlite.org/download.html). 
3. Use `database-dump.sql` to import the example database into your instance
4. Create a dedicated mysql user and grant him permissions to access dum database remotely.
5. Configure database connection details in the following section in `simplemud-generic.py`:
```
# Database connection details
DBhost = 'localhost'
DBport = 3306
DBuser = '<database_user>'
DBpasswd = '<database_password>'
DBdatabase = '<database_name>'
```
6. Run `simplemud-generic.py` using `python3`. You will be greeted by some log entries:
```
13/09/2018 11:51:39 [Server Boot] 
13/09/2018 11:51:39 [info] Rooms loaded: 6
13/09/2018 11:51:39 [info] State Save interval: 10 seconds
13/09/2018 11:51:39 [info] Connecting to database
13/09/2018 11:51:39 [info] NPCs loaded: 3
13/09/2018 11:51:39 [info] Environment Actors loaded: 2
13/09/2018 11:51:39 [info] Items loaded: 2
13/09/2018 11:51:39 [info] Closing database connection
```
7. You can now connect to the server via Telnet on port 35123 (port nubmer is configurable in `mudserver.py`)

## What now?
I'd love to carry on developing this, it has been pretty fun so far. IF anyone feels like they want to take it even further, feel free to get in touch.

## Get in touch
Bartek.Radwanski@gmail.com
